#!/usr/bin/env node
/**
 * Open ETH-PERP LONG on Drift using TypeScript SDK
 */
const { Connection, Keypair } = require('@solana/web3.js');
const { Wallet } = require('@coral-xyz/anchor');
const { DriftClient, BN, PositionDirection, OrderType, MarketType } = require('@drift-labs/sdk');
const fs = require('fs');

const RPC = 'https://api.mainnet-beta.solana.com';

async function openPosition() {
  try {
    // Load keypair
    const keypairData = JSON.parse(fs.readFileSync('.secrets/solana-keypair.json', 'utf8'));
    const keypair = Keypair.fromSecretKey(Uint8Array.from(keypairData));
    
    console.log(`Trading wallet: ${keypair.publicKey.toString()}`);
    
    // Connect
    const connection = new Connection(RPC, 'confirmed');
    const wallet = new Wallet(keypair);
    
    // Initialize Drift client
    console.log('Initializing Drift client...');
    const driftClient = new DriftClient({
      connection,
      wallet,
      env: 'mainnet-beta',
    });
    
    await driftClient.subscribe();
    console.log('✅ Connected to Drift');
    
    // Get ETH market (market index 2)
    const marketIndex = 2;
    const market = driftClient.getPerpMarketAccount(marketIndex);
    
    // Get oracle price
    const oraclePrice = driftClient.getOracleDataForPerpMarket(marketIndex);
    const ethPrice = oraclePrice.price.toNumber() / 1e6;
    console.log(`ETH Oracle Price: $${ethPrice.toFixed(2)}`);
    
    // Calculate position
    // 3x leverage, ~$93 collateral = ~$279 notional
    const collateral = 93;
    const leverage = 3;
    const notional = collateral * leverage;
    const baseSize = notional / ethPrice;
    const baseAmount = new BN(baseSize * 1e9); // BASE_PRECISION
    
    console.log('\nPosition Details:');
    console.log(`  Collateral: $${collateral}`);
    console.log(`  Leverage: ${leverage}x`);
    console.log(`  Notional: $${notional.toFixed(2)}`);
    console.log(`  Size: ${baseSize.toFixed(4)} ETH`);
    
    // Place market order
    console.log('\nPlacing market order...');
    const orderParams = {
      orderType: OrderType.MARKET,
      marketType: MarketType.PERP,
      direction: PositionDirection.LONG,
      baseAssetAmount: baseAmount,
      marketIndex,
    };
    
    const tx = await driftClient.placePerpOrder(orderParams);
    
    console.log('\n✅ ETH LONG OPENED!');
    console.log(`Transaction: ${tx}`);
    console.log(`\nView on Solscan:`);
    console.log(`https://solscan.io/tx/${tx}`);
    console.log(`\nEntry: $${ethPrice.toFixed(2)}`);
    console.log(`Target: $3,370 (+15% = +45% on 3x)`);
    console.log(`Stop: $2,635 (-10% = -30% on 3x)`);
    
    await driftClient.unsubscribe();
    process.exit(0);
    
  } catch (error) {
    console.error('\n❌ ERROR:', error.message);
    console.error(error);
    process.exit(1);
  }
}

console.log('='.repeat(60));
console.log('DRIFT ETH-PERP LONG - 3x LEVERAGE');
console.log('='.repeat(60));
openPosition();
