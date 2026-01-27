#!/usr/bin/env node
/**
 * JUPITER PERPETUALS TRADER
 * Working implementation for BTC/ETH/SOL perps
 */

const { AnchorProvider, Program, Wallet, BN } = require('@coral-xyz/anchor');
const { Connection, Keypair, PublicKey, SystemProgram, TransactionMessage, VersionedTransaction, ComputeBudgetProgram } = require('@solana/web3.js');
const { getAssociatedTokenAddressSync, createAssociatedTokenAccountIdempotentInstruction, createSyncNativeInstruction, createCloseAccountInstruction, NATIVE_MINT } = require('@solana/spl-token');
const fs = require('fs');

// Constants
const RPC_URL = 'https://mainnet.helius-rpc.com/?api-key=54396175-9f9a-418c-b936-2495159cdd0a';
const JUPITER_PERPS_PROGRAM_ID = new PublicKey('PERPHjGBqRHArX4DySjwM6UJHiR3sWAatqfdBS2qQJu');
const JLP_POOL = new PublicKey('5BUwFW4nRbftYTDMbgxykoFWqWHPzahFSNAaaaJtVKsq');

// Custody accounts (collateral)
const CUSTODY = {
  SOL: new PublicKey('7xS2gz2bTp3fwCC7knJvUWTEU9Tycczu6VhJYKgi1wdz'),
  ETH: new PublicKey('AQCGyheWPLeo6Qp9WpYS9m3Qj479t7R636N9ey1rEjEn'),
  BTC: new PublicKey('5Pv3gM9JrFFH883SWAhvJC9RPYmo8UNxuFtv5bMMALkm'),
  USDC: new PublicKey('G18jKKXQwBbrHeiK3C9MRXhkHsLHf7XgCSisykV46EZa'),
};

// Token mints
const MINTS = {
  SOL: NATIVE_MINT,
  ETH: new PublicKey('7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs'), // ETH (Wormhole)
  BTC: new PublicKey('3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh'), // WBTC (Wormhole)
  USDC: new PublicKey('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'),
};

// Load wallet
function loadWallet() {
  const keypairPath = '../drift-bot/.secrets/drift-trading-keypair.json';
  const keypairData = JSON.parse(fs.readFileSync(keypairPath, 'utf8'));
  return Keypair.fromSecretKey(Uint8Array.from(keypairData));
}

// Initialize
async function init() {
  try {
    console.log('Loading wallet...');
    const wallet = loadWallet();
    console.log(`Wallet loaded: ${wallet.publicKey.toString()}`);
    
    console.log('Connecting to RPC...');
    const connection = new Connection(RPC_URL, 'confirmed');
    
    console.log('Creating provider...');
    const provider = new AnchorProvider(connection, new Wallet(wallet), { commitment: 'confirmed' });
    
    console.log('Loading IDL...');
    const idl = JSON.parse(fs.readFileSync('./perpetuals.json', 'utf8'));
    
    console.log('Creating program...');
    const program = new Program(idl, JUPITER_PERPS_PROGRAM_ID, provider);
    
    console.log('✅ Initialization complete\n');
    return { program, wallet, connection, provider };
  } catch (error) {
    console.error('Init error:', error.message);
    throw error;
  }
}

// Derive position PDA
function derivePositionPDA(owner, pool, custody, collateralCustody, side) {
  const sideBuffer = side === 'long' ? Buffer.from([1]) : Buffer.from([2]);
  const [pda] = PublicKey.findProgramAddressSync(
    [
      Buffer.from('position'),
      owner.toBuffer(),
      pool.toBuffer(),
      custody.toBuffer(),
      collateralCustody.toBuffer(),
      sideBuffer
    ],
    JUPITER_PERPS_PROGRAM_ID
  );
  return pda;
}

// Derive position request PDA
function derivePositionRequestPDA(positionPubkey, counter, requestChange) {
  const changeBuffer = requestChange === 'increase' ? Buffer.from([1]) : Buffer.from([2]);
  const [pda] = PublicKey.findProgramAddressSync(
    [
      Buffer.from('position_request'),
      positionPubkey.toBuffer(),
      new BN(counter).toArrayLike(Buffer, 'le', 8),
      changeBuffer
    ],
    JUPITER_PERPS_PROGRAM_ID
  );
  return pda;
}

// Get perpetuals config PDA
function getPerpetualsPDA() {
  const [pda] = PublicKey.findProgramAddressSync(
    [Buffer.from('perpetuals')],
    JUPITER_PERPS_PROGRAM_ID
  );
  return pda;
}

// Open position
async function openPosition(market, direction, sizeUSD, leverage) {
  const { program, wallet, connection } = await init();
  
  console.log('\n🚀 OPENING POSITION');
  console.log('='.repeat(60));
  console.log(`Market: ${market}`);
  console.log(`Direction: ${direction.toUpperCase()}`);
  console.log(`Size: $${sizeUSD}`);
  console.log(`Leverage: ${leverage}x\n`);
  
  try {
    // Get custody and mint
    const custody = CUSTODY[market];
    const collateralCustody = CUSTODY.USDC; // Use USDC as collateral
    const inputMint = MINTS.USDC;
    
    if (!custody) {
      throw new Error(`Unknown market: ${market}`);
    }
    
    // Derive position
    const side = direction === 'long' ? 'long' : 'short';
    const position = derivePositionPDA(wallet.publicKey, JLP_POOL, custody, collateralCustody, side);
    
    // Random counter for unique PDA
    const counter = Math.floor(Math.random() * 1_000_000_000);
    const positionRequest = derivePositionRequestPDA(position, counter, 'increase');
    const perpetuals = getPerpetualsPDA();
    
    // Token accounts
    const positionRequestAta = getAssociatedTokenAddressSync(inputMint, positionRequest, true);
    const fundingAccount = getAssociatedTokenAddressSync(inputMint, wallet.publicKey);
    
    // Calculate amounts
    const collateralAmount = sizeUSD / leverage;
    const collateralTokenDelta = new BN(Math.floor(collateralAmount * 1e6)); // USDC has 6 decimals
    const sizeUsdDelta = new BN(Math.floor(sizeUSD * 1e6));
    const priceSlippage = new BN(Math.floor(3000 * 1e6)); // $3000 slippage for ETH (adjust per market)
    
    console.log(`Collateral: $${collateralAmount} USDC`);
    console.log(`Position size: $${sizeUSD}`);
    
    // Build instruction
    const ix = await program.methods
      .createIncreasePositionMarketRequest({
        counter: new BN(counter),
        collateralTokenDelta,
        jupiterMinimumOut: null, // No swap needed if using USDC
        priceSlippage,
        side: { [side]: {} },
        sizeUsdDelta,
      })
      .accounts({
        owner: wallet.publicKey,
        fundingAccount,
        perpetuals,
        pool: JLP_POOL,
        position,
        custody,
        collateralCustody,
        positionRequest,
        positionRequestAta,
        inputMint,
        referral: null,
      })
      .instruction();
    
    // Get recent blockhash
    const { blockhash } = await connection.getLatestBlockhash();
    
    // Build transaction
    const message = new TransactionMessage({
      payerKey: wallet.publicKey,
      recentBlockhash: blockhash,
      instructions: [
        ComputeBudgetProgram.setComputeUnitPrice({ microLamports: 100000 }),
        ComputeBudgetProgram.setComputeUnitLimit({ units: 1_400_000 }),
        ix
      ],
    }).compileToV0Message();
    
    const tx = new VersionedTransaction(message);
    tx.sign([wallet]);
    
    // Send
    console.log('📤 Sending transaction...');
    const sig = await connection.sendTransaction(tx);
    
    console.log('\n✅ POSITION REQUEST SUBMITTED!');
    console.log(`Signature: ${sig}`);
    console.log(`\nKeepers will execute this within 1-2 minutes`);
    console.log(`Track at: https://solscan.io/tx/${sig}`);
    
    return sig;
    
  } catch (error) {
    console.error('\n❌ ERROR:', error.message);
    if (error.logs) {
      console.error('Program logs:', error.logs);
    }
    throw error;
  }
}

// Get positions (simplified for now)
async function getPositions() {
  try {
    const { program, wallet } = await init();
    
    console.log('\n📊 POSITIONS');
    console.log('='.repeat(60));
    console.log(`Wallet: ${wallet.publicKey.toString()}\n`);
    console.log('To view positions, visit: https://jup.ag/perps');
    console.log('Full position fetching coming in next iteration...\n');
  } catch (error) {
    console.error('Error in getPositions:', error);
    throw error;
  }
}

// Main CLI
const command = process.argv[2];
const args = process.argv.slice(3);

(async () => {
  try {
    console.log('='.repeat(60));
    console.log('JUPITER PERPETUALS TRADER v0.1');
    console.log('='.repeat(60));
    
    switch (command) {
      case 'positions':
        await getPositions();
        break;
        
      case 'long':
      case 'short':
        const market = (args[0] || '').toUpperCase();
        const sizeUSD = parseFloat(args[1]) || 100;
        const leverage = parseInt(args[2]) || 10;
        await openPosition(market, command, sizeUSD, leverage);
        break;
        
      default:
        console.log('\n📖 USAGE:');
        console.log('  node jup_perps.js positions');
        console.log('  node jup_perps.js long ETH 100 5    # $100 position, 5x leverage');
        console.log('  node jup_perps.js short BTC 200 10  # $200 short, 10x');
        console.log('\nSupported: SOL, ETH, BTC');
        console.log('Leverage: 1x to 100x');
    }
    
    process.exit(0);
    
  } catch (error) {
    console.error('\n❌ FAILED:', error.message);
    process.exit(1);
  }
})();
