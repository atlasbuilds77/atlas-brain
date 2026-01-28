#!/usr/bin/env node

/**
 * Jupiter Perps Position Checker V2
 * Uses Anchor program to properly decode position data
 * NO BROWSER REQUIRED - works in automated cron jobs
 */

const { AnchorProvider, BN, Program, Wallet } = require("@coral-xyz/anchor");
const { Connection, Keypair, PublicKey } = require("@solana/web3.js");
const fs = require("fs").promises;
const path = require("path");

// Load the Jupiter Perpetuals IDL
const IDL = require("./jupiter-perps-idl.json");

// Jupiter Perpetuals Program ID
const JUPITER_PERPETUALS_PROGRAM_ID = new PublicKey(
  "PERPHjGBqRHArX4DySjwM6UJHiR3sWAatqfdBS2qQJu"
);

// RPC connection
const RPC_URL = process.env.SOLANA_RPC_URL || "https://api.mainnet-beta.solana.com";
const connection = new Connection(RPC_URL, "confirmed");

// Wallet address to check
const WALLET_ADDRESS = process.env.JUPITER_WALLET || "28Gv5ncMyeS5oHYgsBd9r857dpvRKqw5ttc1nKN6UxXj";

// Custody addresses (to identify tokens)
const CUSTODY_MAP = {
  "7xS2gz2bTp3fwCC7knJvUWTEU9Tycczu6VhJYKgi1wdz": "SOL",
  "AQCGyheWPLeo6Qp9WpYS9m3Qj479t7R636N9ey1rEjEn": "ETH",
  "5Pv3gM9JrFFH883SWAhvJC9RPYmo8UNxuFtv5bMMALkm": "BTC",
  "G18jKKXQwBbrHeiK3C9MRXhkHsLHf7XgCSisykV46EZa": "USDC",
  "4vkNeXiYEUizLdrpdPS1eC2mccyM4NUPRtERrk6ZETkk": "USDT",
};

// Helper: Format BN to USD string
function formatUSD(value, decimals = 6) {
  if (!value || value.isZero()) return "0.00";
  const divisor = new BN(10).pow(new BN(decimals));
  const num = value.div(divisor).toNumber() + value.mod(divisor).toNumber() / divisor.toNumber();
  return num.toFixed(2);
}

// Get positions for a wallet using Anchor
async function getPositionsForWallet(walletAddress) {
  try {
    console.log(`Fetching positions for wallet: ${walletAddress}`);
    console.log(`Using RPC: ${RPC_URL}\n`);

    // Create Anchor program
    const provider = new AnchorProvider(
      connection,
      new Wallet(Keypair.generate()), // Dummy wallet for reading
      { commitment: "confirmed" }
    );
    
    const program = new Program(IDL, JUPITER_PERPETUALS_PROGRAM_ID, provider);
    const walletPubkey = new PublicKey(walletAddress);
    
    // Query position accounts for this wallet
    const accounts = await connection.getProgramAccounts(
      program.programId,
      {
        commitment: "confirmed",
        filters: [
          {
            memcmp: {
              offset: 8, // owner field offset
              bytes: walletPubkey.toBase58()
            }
          }
        ]
      }
    );
    
    console.log(`Found ${accounts.length} accounts for wallet`);
    
    const positions = [];
    
    for (const { pubkey, account } of accounts) {
      try {
        // Try to decode as Position account
        const position = program.coder.accounts.decode("position", account.data);
        
        // Skip closed positions (sizeUsd = 0)
        if (position.sizeUsd.isZero()) {
          continue;
        }
        
        // Get token symbol
        const custodyKey = position.custody.toBase58();
        const token = CUSTODY_MAP[custodyKey] || "UNKNOWN";
        
        // Calculate leverage
        const leverage = position.sizeUsd.mul(new BN(100)).div(position.collateralUsd);
        
        // Format side
        const side = position.side.long ? "LONG" : "SHORT";
        
        positions.push({
          pubkey: pubkey.toBase58(),
          token,
          side,
          entryPrice: formatUSD(position.price),
          sizeUsd: formatUSD(position.sizeUsd),
          collateralUsd: formatUSD(position.collateralUsd),
          leverage: leverage.toNumber() / 100,
          openTime: new Date(position.openTime.toNumber() * 1000),
          updateTime: new Date(position.updateTime.toNumber() * 1000),
          raw: position
        });
      } catch (err) {
        // Not a position account, skip
        continue;
      }
    }
    
    return positions;
  } catch (error) {
    console.error("Error fetching positions:", error);
    throw error;
  }
}

// Get current price from a simple API
async function getCurrentPrice(token) {
  try {
    // Use CoinGecko API (free, no auth needed)
    const symbolMap = {
      ETH: "ethereum",
      SOL: "solana",
      BTC: "bitcoin"
    };
    
    const coinId = symbolMap[token];
    if (!coinId) return 0;
    
    const response = await fetch(
      `https://api.coingecko.com/api/v3/simple/price?ids=${coinId}&vs_currencies=usd`
    );
    const data = await response.json();
    return data[coinId]?.usd || 0;
  } catch (error) {
    console.error(`Error fetching price for ${token}:`, error.message);
    return 0;
  }
}

// Calculate P&L for a position
async function calculatePnL(position) {
  const currentPrice = await getCurrentPrice(position.token);
  if (currentPrice === 0) {
    return { pnl: "N/A", pnlPercent: "N/A", currentPrice: "N/A" };
  }
  
  const entryPrice = parseFloat(position.entryPrice);
  const sizeUsd = parseFloat(position.sizeUsd);
  const collateralUsd = parseFloat(position.collateralUsd);
  
  let priceDelta, hasProfit;
  if (position.side === "LONG") {
    priceDelta = currentPrice - entryPrice;
    hasProfit = currentPrice > entryPrice;
  } else {
    priceDelta = entryPrice - currentPrice;
    hasProfit = entryPrice > currentPrice;
  }
  
  const pnl = (sizeUsd * priceDelta) / entryPrice;
  const pnlPercent = (pnl / collateralUsd) * 100;
  
  return {
    currentPrice: currentPrice.toFixed(2),
    pnl: (hasProfit ? "+" : "") + pnl.toFixed(2),
    pnlPercent: (hasProfit ? "+" : "") + pnlPercent.toFixed(2) + "%",
    hasProfit
  };
}

// Update position file
async function updatePositionFile(positions) {
  const now = new Date();
  const pstTime = new Intl.DateTimeFormat("en-US", {
    timeZone: "America/Los_Angeles",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false
  }).format(now);
  
  let content = `# Jupiter Perps Positions\n\n`;
  content += `**Last Updated:** ${pstTime} PST\n`;
  content += `**Wallet:** ${WALLET_ADDRESS}\n`;
  content += `**Total Positions:** ${positions.length}\n\n`;
  
  if (positions.length === 0) {
    content += `No open positions.\n`;
  } else {
    for (const pos of positions) {
      const pnl = await calculatePnL(pos);
      
      content += `## ${pos.token} ${pos.leverage.toFixed(2)}x ${pos.side}\n\n`;
      content += `- **Entry Price:** $${pos.entryPrice}\n`;
      content += `- **Current Price:** $${pnl.currentPrice}\n`;
      content += `- **Size:** $${pos.sizeUsd}\n`;
      content += `- **Collateral:** $${pos.collateralUsd}\n`;
      content += `- **P&L:** $${pnl.pnl} (${pnl.pnlPercent})\n`;
      content += `- **Opened:** ${pos.openTime.toISOString()}\n`;
      content += `- **Last Update:** ${pos.updateTime.toISOString()}\n`;
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
        console.log(`${pos.token} ${pos.leverage.toFixed(2)}x ${pos.side}`);
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
    console.error(error.stack);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = { getPositionsForWallet, calculatePnL };
