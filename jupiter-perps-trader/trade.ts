#!/usr/bin/env ts-node
/**
 * JUPITER PERPS TRADER
 * Simple wrapper for opening/closing positions
 */

import { Keypair, Connection, PublicKey, TransactionMessage, VersionedTransaction, ComputeBudgetProgram, SystemProgram, TransactionInstruction } from "@solana/web3.js";
import { CUSTODY_PUBKEY, JUPITER_PERPETUALS_PROGRAM, RPC_CONNECTION, JUPITER_PERPETUALS_PROGRAM_ID, JLP_POOL_ACCOUNT_PUBKEY } from "./src/constants.ts";
import fs from "fs";
import { AnchorProvider, BN, Wallet } from "@coral-xyz/anchor";
import { createAssociatedTokenAccountIdempotentInstruction, createCloseAccountInstruction, createSyncNativeInstruction, getAssociatedTokenAddressSync, NATIVE_MINT } from "@solana/spl-token";
import { generatePositionRequestPda } from "./src/examples/generate-position-and-position-request-pda.ts";

// Load wallet
function loadWallet(): Keypair {
  const keypairPath = '../drift-bot/.secrets/drift-trading-keypair.json';
  const keypairData = JSON.parse(fs.readFileSync(keypairPath, 'utf8'));
  return Keypair.fromSecretKey(Uint8Array.from(keypairData));
}

// Get custody account for a market
async function getCustodyAccount(market: string) {
  const custodyMap: Record<string, string> = {
    'SOL': CUSTODY_PUBKEY.SOL,
    'ETH': CUSTODY_PUBKEY.ETH,
    'BTC': CUSTODY_PUBKEY.BTC,
  };
  
  const custodyAddress = custodyMap[market.toUpperCase()];
  if (!custodyAddress) {
    throw new Error(`Unknown market: ${market}. Use SOL, ETH, or BTC`);
  }
  
  const custody = await JUPITER_PERPETUALS_PROGRAM.account.custody.fetch(
    new PublicKey(custodyAddress)
  );
  
  return {
    publicKey: new PublicKey(custodyAddress),
    account: custody
  };
}

// Get open positions for wallet
async function getPositions(wallet: PublicKey) {
  const gpaResult = await RPC_CONNECTION.getProgramAccounts(
    JUPITER_PERPETUALS_PROGRAM.programId,
    {
      commitment: "confirmed",
      filters: [
        {
          memcmp: {
            bytes: wallet.toBase58(),
            offset: 8,
          },
        },
        {
          memcmp: JUPITER_PERPETUALS_PROGRAM.coder.accounts.memcmp("position"),
        },
      ],
    },
  );

  const positions = gpaResult.map((item) => {
    return {
      publicKey: item.pubkey,
      account: JUPITER_PERPETUALS_PROGRAM.coder.accounts.decode(
        "position",
        item.account.data,
      ),
    };
  });

  return positions.filter((position) => position.account.sizeUsd.gtn(0));
}

// Get pending position requests for wallet
async function getPendingRequests(wallet: PublicKey) {
  const gpaResult = await RPC_CONNECTION.getProgramAccounts(
    JUPITER_PERPETUALS_PROGRAM.programId,
    {
      commitment: "confirmed",
      filters: [
        {
          memcmp: {
            bytes: wallet.toBase58(),
            offset: 8, // owner field offset
          },
        },
        {
          memcmp: JUPITER_PERPETUALS_PROGRAM.coder.accounts.memcmp("positionRequest"),
        },
      ],
    },
  );

  const requests = gpaResult.map((item) => {
    return {
      publicKey: item.pubkey,
      account: JUPITER_PERPETUALS_PROGRAM.coder.accounts.decode(
        "positionRequest",
        item.account.data,
      ),
    };
  });

  return requests;
}

// Open a position
async function openPosition(market: string, side: 'long' | 'short', sizeUsd: number, collateralSol: number) {
  const wallet = loadWallet();
  console.log(`\n🔥 Opening ${side.toUpperCase()} position on ${market}`);
  console.log(`   Size: $${sizeUsd} USD`);
  console.log(`   Collateral: ${collateralSol} SOL`);
  console.log(`   Wallet: ${wallet.publicKey.toString()}`);
  
  // Get custody accounts
  const custody = await getCustodyAccount(market);
  const collateralCustody = await getCustodyAccount('SOL'); // Always use SOL as collateral
  
  // Generate position PDA
  const positionPda = PublicKey.findProgramAddressSync(
    [
      Buffer.from("position"),
      wallet.publicKey.toBuffer(),
      JLP_POOL_ACCOUNT_PUBKEY.toBuffer(),
      custody.publicKey.toBuffer(),
      collateralCustody.publicKey.toBuffer(),
      side === 'long' ? [1] : [2], // Side enum
    ],
    JUPITER_PERPETUALS_PROGRAM_ID
  )[0];
  
  console.log(`   Position PDA: ${positionPda.toString()}`);
  
  // Generate position request PDA
  const { positionRequest, counter } = generatePositionRequestPda({
    positionPubkey: positionPda,
    requestChange: "increase",
  });
  
  // Setup token accounts
  const inputMint = NATIVE_MINT; // wSOL
  const positionRequestAta = getAssociatedTokenAddressSync(inputMint, positionRequest, true);
  const fundingAccount = getAssociatedTokenAddressSync(inputMint, wallet.publicKey);
  
  // Convert amounts
  const collateralLamports = new BN(collateralSol * 1e9);
  const sizeUsdBn = new BN(sizeUsd * 1e6); // USDC has 6 decimals
  const priceSlippage = new BN(0.05 * 1e6); // 5% slippage scaled to 6 decimals
  
  // Build instructions
  const preInstructions: TransactionInstruction[] = [];
  const postInstructions: TransactionInstruction[] = [];
  
  // Wrap SOL to wSOL
  preInstructions.push(
    createAssociatedTokenAccountIdempotentInstruction(
      wallet.publicKey,
      fundingAccount,
      wallet.publicKey,
      NATIVE_MINT
    )
  );
  
  preInstructions.push(
    SystemProgram.transfer({
      fromPubkey: wallet.publicKey,
      toPubkey: fundingAccount,
      lamports: BigInt(collateralLamports.toString()),
    })
  );
  
  preInstructions.push(createSyncNativeInstruction(fundingAccount));
  postInstructions.push(createCloseAccountInstruction(fundingAccount, wallet.publicKey, wallet.publicKey));
  
  // Create increase position instruction
  const increaseIx = await JUPITER_PERPETUALS_PROGRAM.methods
    .createIncreasePositionMarketRequest({
      counter,
      collateralTokenDelta: collateralLamports,
      jupiterMinimumOut: null, // No swap needed (using wSOL directly)
      priceSlippage,
      side: { [side]: {} },
      sizeUsdDelta: sizeUsdBn,
    })
    .accounts({
      custody: custody.publicKey,
      collateralCustody: collateralCustody.publicKey,
      fundingAccount,
      inputMint,
      owner: wallet.publicKey,
      perpetuals: PublicKey.findProgramAddressSync(
        [Buffer.from("perpetuals")],
        JUPITER_PERPETUALS_PROGRAM_ID
      )[0],
      pool: JLP_POOL_ACCOUNT_PUBKEY,
      position: positionPda,
      positionRequest,
      positionRequestAta,
      referral: null,
    })
    .instruction();
  
  // Get recent blockhash
  const { blockhash, lastValidBlockHeight } = await RPC_CONNECTION.getLatestBlockhash();
  
  // Build transaction
  const instructions = [
    ComputeBudgetProgram.setComputeUnitPrice({ microLamports: 100000 }),
    ComputeBudgetProgram.setComputeUnitLimit({ units: 1_400_000 }),
    ...preInstructions,
    increaseIx,
    ...postInstructions,
  ];
  
  const txMessage = new TransactionMessage({
    payerKey: wallet.publicKey,
    recentBlockhash: blockhash,
    instructions,
  }).compileToV0Message();
  
  const tx = new VersionedTransaction(txMessage);
  tx.sign([wallet]);
  
  // Send transaction
  console.log(`\n📤 Sending transaction...`);
  const signature = await RPC_CONNECTION.sendTransaction(tx, {
    skipPreflight: false,
    maxRetries: 3,
  });
  
  console.log(`\n✅ Position request submitted!`);
  console.log(`   Signature: ${signature}`);
  console.log(`   Explorer: https://solscan.io/tx/${signature}`);
  console.log(`\n⏳ Waiting for keeper to fulfill request...`);
  
  // Wait for confirmation
  await RPC_CONNECTION.confirmTransaction({
    signature,
    blockhash,
    lastValidBlockHeight,
  });
  
  console.log(`✅ Transaction confirmed!`);
  console.log(`\nPosition will be opened by keeper. Check position with: ts-node trade.ts positions`);
}

// Close a position
async function closePosition(positionPubkey: string) {
  const wallet = loadWallet();
  console.log(`\n🔥 Closing position: ${positionPubkey}`);
  
  const positionPda = new PublicKey(positionPubkey);
  const position = await JUPITER_PERPETUALS_PROGRAM.account.position.fetch(positionPda);
  
  // Generate position request PDA
  const { positionRequest, counter } = generatePositionRequestPda({
    positionPubkey: positionPda,
    requestChange: "decrease",
  });
  
  const desiredMint = NATIVE_MINT; // Receive wSOL
  const receivingAccount = getAssociatedTokenAddressSync(desiredMint, wallet.publicKey, true);
  const positionRequestAta = getAssociatedTokenAddressSync(desiredMint, positionRequest, true);
  
  const postInstructions: TransactionInstruction[] = [];
  postInstructions.push(
    createCloseAccountInstruction(receivingAccount, wallet.publicKey, wallet.publicKey)
  );
  
  // Create decrease position instruction
  const decreaseIx = await JUPITER_PERPETUALS_PROGRAM.methods
    .createDecreasePositionMarketRequest({
      collateralUsdDelta: new BN(0),
      sizeUsdDelta: new BN(0),
      priceSlippage: new BN(100_000_000_000), // High slippage to ensure execution
      jupiterMinimumOut: null,
      counter,
      entirePosition: true,
    })
    .accounts({
      owner: wallet.publicKey,
      receivingAccount,
      perpetuals: PublicKey.findProgramAddressSync(
        [Buffer.from("perpetuals")],
        JUPITER_PERPETUALS_PROGRAM_ID
      )[0],
      pool: JLP_POOL_ACCOUNT_PUBKEY,
      position: positionPda,
      positionRequest,
      positionRequestAta,
      custody: position.custody,
      collateralCustody: position.collateralCustody,
      desiredMint,
      referral: null,
    })
    .instruction();
  
  // Get recent blockhash
  const { blockhash, lastValidBlockHeight } = await RPC_CONNECTION.getLatestBlockhash();
  
  // Build transaction
  const instructions = [
    ComputeBudgetProgram.setComputeUnitPrice({ microLamports: 100000 }),
    ComputeBudgetProgram.setComputeUnitLimit({ units: 1_400_000 }),
    decreaseIx,
    ...postInstructions,
  ];
  
  const txMessage = new TransactionMessage({
    payerKey: wallet.publicKey,
    recentBlockhash: blockhash,
    instructions,
  }).compileToV0Message();
  
  const tx = new VersionedTransaction(txMessage);
  tx.sign([wallet]);
  
  // Send transaction
  console.log(`\n📤 Sending transaction...`);
  const signature = await RPC_CONNECTION.sendTransaction(tx, {
    skipPreflight: false,
    maxRetries: 3,
  });
  
  console.log(`\n✅ Close request submitted!`);
  console.log(`   Signature: ${signature}`);
  console.log(`   Explorer: https://solscan.io/tx/${signature}`);
  console.log(`\n⏳ Waiting for keeper to fulfill request...`);
  
  // Wait for confirmation
  await RPC_CONNECTION.confirmTransaction({
    signature,
    blockhash,
    lastValidBlockHeight,
  });
  
  console.log(`✅ Transaction confirmed!`);
  console.log(`\nPosition will be closed by keeper.`);
}

// Main command handler
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  console.log('='.repeat(60));
  console.log('JUPITER PERPETUALS TRADER v1.0');
  console.log('='.repeat(60));
  
  try {
    if (command === 'test') {
      const wallet = loadWallet();
      console.log(`\n✅ Wallet loaded: ${wallet.publicKey.toString()}`);
      console.log(`✅ RPC connected: ${RPC_CONNECTION.rpcEndpoint}`);
      console.log(`✅ Jupiter Perps Program: ${JUPITER_PERPETUALS_PROGRAM.programId.toString()}`);
      console.log(`\nAvailable markets:`);
      console.log(`  - SOL: ${CUSTODY_PUBKEY.SOL}`);
      console.log(`  - ETH: ${CUSTODY_PUBKEY.ETH}`);
      console.log(`  - BTC: ${CUSTODY_PUBKEY.BTC}`);
      console.log(`\n✅ Ready to trade!`);
    } 
    else if (command === 'positions') {
      const wallet = loadWallet();
      const positions = await getPositions(wallet.publicKey);
      
      console.log(`\n📊 Open positions for ${wallet.publicKey.toString()}:`);
      
      if (positions.length === 0) {
        console.log(`   No open positions`);
      } else {
        for (const pos of positions) {
          const sizeUsd = pos.account.sizeUsd.toNumber() / 1e6;
          const collateralUsd = pos.account.collateralUsd.toNumber() / 1e6;
          const leverage = sizeUsd / collateralUsd;
          const side = pos.account.side.long ? 'LONG' : 'SHORT';
          
          console.log(`\n   Position: ${pos.publicKey.toString()}`);
          console.log(`   Side: ${side}`);
          console.log(`   Size: $${sizeUsd.toFixed(2)}`);
          console.log(`   Collateral: $${collateralUsd.toFixed(2)}`);
          console.log(`   Leverage: ${leverage.toFixed(2)}x`);
        }
      }
    }
    else if (command === 'pending') {
      const wallet = loadWallet();
      const requests = await getPendingRequests(wallet.publicKey);
      
      console.log(`\n⏳ Pending position requests for ${wallet.publicKey.toString()}:`);
      
      if (requests.length === 0) {
        console.log(`   No pending requests`);
      } else {
        for (const req of requests) {
          const requestType = req.account.requestChange.increase ? 'OPEN' : 
                             req.account.requestChange.decrease ? 'CLOSE' : 'UPDATE';
          const side = req.account.side?.long ? 'LONG' : 
                      req.account.side?.short ? 'SHORT' : 'N/A';
          const sizeUsd = req.account.sizeUsdDelta ? req.account.sizeUsdDelta.toNumber() / 1e6 : 0;
          const collateral = req.account.collateralDelta ? req.account.collateralDelta.toNumber() / 1e9 : 0;
          
          console.log(`\n   Request: ${req.publicKey.toString()}`);
          console.log(`   Type: ${requestType}`);
          console.log(`   Side: ${side}`);
          console.log(`   Size: $${sizeUsd.toFixed(2)}`);
          console.log(`   Collateral: ${collateral.toFixed(4)} SOL`);
          console.log(`   Counter: ${req.account.counter}`);
        }
      }
    }
    else if (command === 'long' || command === 'short') {
      const market = args[1];
      const sizeUsd = parseFloat(args[2]);
      const collateralSol = parseFloat(args[3]);
      
      if (!market || !sizeUsd || !collateralSol) {
        throw new Error('Usage: ts-node trade.ts long/short <market> <sizeUsd> <collateralSol>');
      }
      
      await openPosition(market, command, sizeUsd, collateralSol);
    }
    else if (command === 'close') {
      const positionPubkey = args[1];
      
      if (!positionPubkey) {
        throw new Error('Usage: ts-node trade.ts close <positionPubkey>');
      }
      
      await closePosition(positionPubkey);
    }
    else {
      console.log('\n📖 USAGE:');
      console.log('  ts-node trade.ts test                              # Test connection');
      console.log('  ts-node trade.ts positions                         # Show open positions');
      console.log('  ts-node trade.ts pending                           # Show pending requests');
      console.log('  ts-node trade.ts long SOL 100 0.4                  # Open long $100 with 0.4 SOL collateral');
      console.log('  ts-node trade.ts short ETH 200 0.8                 # Open short $200 with 0.8 SOL collateral');
      console.log('  ts-node trade.ts close <position_pubkey>           # Close position');
      console.log();
    }
  } catch (error) {
    console.error('\n❌ Error:', error);
    process.exit(1);
  }
}

main().catch(console.error);
