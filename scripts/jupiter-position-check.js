#!/usr/bin/env node

/**
 * Jupiter Perps Position Checker
 * Queries on-chain position data for a wallet address
 * NO BROWSER REQUIRED - works in automated cron jobs
 */

const { AnchorProvider, BN, Program, Wallet } = require("@coral-xyz/anchor");
const { Connection, Keypair, PublicKey } = require("@solana/web3.js");
const fs = require("fs").promises;
const path = require("path");

// Jupiter Perpetuals Program ID
const JUPITER_PERPETUALS_PROGRAM_ID = new PublicKey(
  "PERPHjGBqRHArX4DySjwM6UJHiR3sWAatqfdBS2qQJu"
);

// RPC connection (using public endpoint, consider upgrading for production)
const RPC_URL = process.env.SOLANA_RPC_URL || "https://api.mainnet-beta.solana.com";
const connection = new Connection(RPC_URL, "confirmed");

// Wallet address to check (Orion's Jupiter embedded wallet)
const WALLET_ADDRESS = process.env.JUPITER_WALLET || "28Gv5ncMyeS5oHYgsBd9r857dpvRKqw5ttc1nKN6UxXj";

// Helper: Format BN to USD string (handles large numbers)
function formatUSD(value, decimals = 6, displayDecimals = 2) {
  const divisor = new BN(10).pow(new BN(decimals));
  const quotient = value.div(divisor);
  const remainder = value.mod(divisor);
  
  // Build decimal part
  const decimal = remainder.toString().padStart(decimals, '0').slice(0, displayDecimals);
  
  return `${quotient.toString()}.${decimal}`;
}

// Helper: Format BN to percentage
function formatPercent(value, decimals = 6) {
  const num = value.toNumber() / Math.pow(10, decimals);
  return (num * 100).toFixed(2);
}

// Load IDL (using a minimal version for now)
async function loadIDL() {
  // Minimal IDL with just Position account structure
  return {
    version: "0.1.0",
    name: "perpetuals",
    accounts: [
      {
        name: "position",
        discriminator: [170, 188, 143, 228, 122, 64, 247, 208]
      }
    ]
  };
}

// Get positions for a wallet
async function getPositionsForWallet(walletAddress) {
  try {
    console.log(`Fetching positions for wallet: ${walletAddress}`);
    console.log(`Using RPC: ${RPC_URL}\n`);

    const walletPubkey = new PublicKey(walletAddress);
    
    // Query all position accounts
    // Position accounts have the wallet's pubkey at offset 8 (after discriminator)
    // First try filtering by wallet only (more reliable)
    const accounts = await connection.getProgramAccounts(
      JUPITER_PERPETUALS_PROGRAM_ID,
      {
        commitment: "confirmed",
        filters: [
          {
            // Filter by owner (wallet address at offset 8)
            memcmp: {
              offset: 8,
              bytes: walletPubkey.toBase58()
            }
          }
        ]
      }
    );
    
    // Filter for position accounts by discriminator (aabc8fe47a40f7d0)
    const positionDiscriminator = Buffer.from([170, 188, 143, 228, 122, 64, 247, 208]);
    const positionAccounts = accounts.filter(acc => {
      const disc = acc.account.data.slice(0, 8);
      return disc.equals(positionDiscriminator);
    });

    console.log(`Found ${accounts.length} total accounts for wallet`);
    console.log(`Found ${positionAccounts.length} position accounts (including closed)`);

    const positions = [];
    
    for (const { pubkey, account } of positionAccounts) {
      // Parse position data manually
      const data = account.data;
      
      // Skip discriminator (8 bytes)
      let offset = 8;
      
      // owner (32 bytes)
      const owner = new PublicKey(data.slice(offset, offset + 32));
      offset += 32;
      
      // pool (32 bytes)
      const pool = new PublicKey(data.slice(offset, offset + 32));
      offset += 32;
      
      // custody (32 bytes) - this tells us which token (SOL/ETH/BTC)
      const custody = new PublicKey(data.slice(offset, offset + 32));
      offset += 32;
      
      // collateralCustody (32 bytes)
      const collateralCustody = new PublicKey(data.slice(offset, offset + 32));
      offset += 32;
      
      // openTime (8 bytes, i64)
      const openTime = new BN(data.slice(offset, offset + 8), "le");
      offset += 8;
      
      // updateTime (8 bytes, i64)
      const updateTime = new BN(data.slice(offset, offset + 8), "le");
      offset += 8;
      
      // side (1 byte + 1 byte padding) - 0 = long, 1 = short
      const side = data[offset] === 0 ? "long" : "short";
      offset += 2;
      
      // price (8 bytes, u64)
      const price = new BN(data.slice(offset, offset + 8), "le");
      offset += 8;
      
      // sizeUsd (8 bytes, u64)
      const sizeUsd = new BN(data.slice(offset, offset + 8), "le");
      offset += 8;
      
      // collateralUsd (8 bytes, u64)
      const collateralUsd = new BN(data.slice(offset, offset + 8), "le");
      offset += 8;
      
      // Skip if position is closed (sizeUsd = 0)
      if (sizeUsd.isZero()) {
        continue;
      }
      
      // Determine token based on custody address
      let token = "UNKNOWN";
      const custodyStr = custody.toBase58();
      if (custodyStr === "7xS2gz2bTp3fwCC7knJvUWTEU9Tycczu6VhJYKgi1wdz") token = "SOL";
      else if (custodyStr === "AQCGyheWPLeo6Qp9WpYS9m3Qj479t7R636N9ey1rEjEn") token = "ETH";
      else if (custodyStr === "5Pv3gM9JrFFH883SWAhvJC9RPYmo8UNxuFtv5bMMALkm") token = "BTC";
      
      // Calculate leverage
      const leverage = sizeUsd.mul(new BN(100)).div(collateralUsd).toNumber() / 100;
      
      positions.push({
        pubkey: pubkey.toBase58(),
        owner: owner.toBase58(),
        token,
        side,
        entryPrice: formatUSD(price, 6, 2),
        sizeUsd: formatUSD(sizeUsd, 6, 2),
        collateralUsd: formatUSD(collateralUsd, 6, 2),
        leverage: leverage.toFixed(2) + "x",
        openTime: new Date(openTime.toNumber() * 1000).toISOString(),
        updateTime: new Date(updateTime.toNumber() * 1000).toISOString(),
        raw: {
          price,
          sizeUsd,
          collateralUsd,
          custody: custodyStr
        }
      });
    }

    return positions;
  } catch (error) {
    console.error("Error fetching positions:", error);
    throw error;
  }
}

// Get current price for a token (simplified - using a price feed)
async function getCurrentPrice(token) {
  // For now, return approximate prices
  // TODO: Integrate with Pyth oracle or Jupiter price API
  const prices = {
    ETH: 3100,
    SOL: 200,
    BTC: 98000
  };
  return prices[token] || 0;
}

// Calculate P&L for a position
async function calculatePnL(position) {
  const currentPrice = await getCurrentPrice(position.token);
  if (currentPrice === 0) {
    return { pnl: "N/A", pnlPercent: "N/A", currentPrice: "N/A" };
  }
  
  const entryPrice = parseFloat(position.entryPrice);
  const sizeUsd = parseFloat(position.sizeUsd);
  
  let priceDelta, hasProfit;
  if (position.side === "long") {
    priceDelta = currentPrice - entryPrice;
    hasProfit = currentPrice > entryPrice;
  } else {
    priceDelta = entryPrice - currentPrice;
    hasProfit = entryPrice > currentPrice;
  }
  
  const pnl = (sizeUsd * priceDelta) / entryPrice;
  const pnlPercent = (pnl / parseFloat(position.collateralUsd)) * 100;
  
  return {
    currentPrice: currentPrice.toFixed(2),
    pnl: (hasProfit ? "+" : "") + pnl.toFixed(2),
    pnlPercent: (hasProfit ? "+" : "") + pnlPercent.toFixed(2) + "%",
    hasProfit
  };
}

// Update active-positions.md file
async function updatePositionFile(positions) {
  const timestamp = new Date().toISOString().replace("T", " ").split(".")[0] + " PST";
  
  let content = `# Jupiter Perps Positions\n\n`;
  content += `**Last Updated:** ${timestamp}\n`;
  content += `**Wallet:** ${WALLET_ADDRESS}\n`;
  content += `**Total Positions:** ${positions.length}\n\n`;
  
  if (positions.length === 0) {
    content += `No open positions.\n`;
  } else {
    for (const pos of positions) {
      const pnl = await calculatePnL(pos);
      
      content += `## ${pos.token} ${pos.leverage} ${pos.side.toUpperCase()}\n\n`;
      content += `- **Entry Price:** $${pos.entryPrice}\n`;
      content += `- **Current Price:** $${pnl.currentPrice}\n`;
      content += `- **Size:** $${pos.sizeUsd}\n`;
      content += `- **Collateral:** $${pos.collateralUsd}\n`;
      content += `- **P&L:** $${pnl.pnl} (${pnl.pnlPercent})\n`;
      content += `- **Opened:** ${pos.openTime}\n`;
      content += `- **Last Update:** ${pos.updateTime}\n`;
      content += `- **Address:** \`${pos.pubkey}\`\n\n`;
    }
  }
  
  const filePath = path.join(__dirname, "..", "memory", "trading", "jupiter-positions-latest.md");
  await fs.writeFile(filePath, content, "utf8");
  console.log(`\n✅ Updated: ${filePath}`);
  
  return content;
}

// Main function
async function main() {
  try {
    console.log("=== Jupiter Perps Position Check ===\n");
    
    const positions = await getPositionsForWallet(WALLET_ADDRESS);
    
    console.log(`\n📊 RESULTS:\n`);
    
    if (positions.length === 0) {
      console.log("No open positions found.");
    } else {
      for (const pos of positions) {
        const pnl = await calculatePnL(pos);
        console.log(`${pos.token} ${pos.leverage} ${pos.side.toUpperCase()}`);
        console.log(`  Entry: $${pos.entryPrice} | Current: $${pnl.currentPrice}`);
        console.log(`  Size: $${pos.sizeUsd} | Collateral: $${pos.collateralUsd}`);
        console.log(`  P&L: $${pnl.pnl} (${pnl.pnlPercent})`);
        console.log("");
      }
    }
    
    await updatePositionFile(positions);
    
    console.log("\n✅ Position check complete!");
    
  } catch (error) {
    console.error("\n❌ Error:", error.message);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = { getPositionsForWallet, calculatePnL };
