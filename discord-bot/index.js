#!/usr/bin/env node
/**
 * Standalone Discord Bot for Clawdbot Integration
 * Connects to Discord, listens in channels, calls Clawdbot API for responses
 * Uses Haiku model for cost efficiency
 */

const { Client, GatewayIntentBits } = require('discord.js');
const axios = require('axios');

// ============================================================================
// CONFIGURATION
// ============================================================================

const CONFIG = {
  // Discord Bot Token - REPLACE THIS
  DISCORD_TOKEN: process.env.DISCORD_TOKEN || 'YOUR_BOT_TOKEN_HERE',
  
  // Clawdbot Gateway URL
  CLAWDBOT_URL: process.env.CLAWDBOT_URL || 'http://localhost:3000',
  
  // Clawdbot API Token (if auth enabled)
  CLAWDBOT_TOKEN: process.env.CLAWDBOT_TOKEN || '',
  
  // Model to use (haiku for cheap)
  MODEL: process.env.MODEL || 'anthropic/claude-haiku-3.5',
  
  // Channels to listen in (leave empty for all channels bot can see)
  ALLOWED_CHANNELS: (process.env.ALLOWED_CHANNELS || '').split(',').filter(Boolean),
  
  // Response prefix (optional, e.g., "[Atlas]")
  RESPONSE_PREFIX: process.env.RESPONSE_PREFIX || '',
};

// ============================================================================
// DISCORD CLIENT SETUP
// ============================================================================

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.DirectMessages,
  ],
});

// ============================================================================
// CLAWDBOT API INTEGRATION
// ============================================================================

async function callClawdbot(message) {
  try {
    const headers = {
      'Content-Type': 'application/json',
    };
    
    if (CONFIG.CLAWDBOT_TOKEN) {
      headers['Authorization'] = `Bearer ${CONFIG.CLAWDBOT_TOKEN}`;
    }
    
    const payload = {
      message: message.content,
      model: CONFIG.MODEL,
      metadata: {
        platform: 'discord',
        channelId: message.channel.id,
        channelName: message.channel.name || 'DM',
        authorId: message.author.id,
        authorTag: message.author.tag,
        messageId: message.id,
        guildId: message.guild?.id,
        guildName: message.guild?.name,
      },
    };
    
    const response = await axios.post(
      `${CONFIG.CLAWDBOT_URL}/api/chat`,
      payload,
      { headers, timeout: 60000 }
    );
    
    return response.data.response || response.data.message || 'No response';
  } catch (error) {
    console.error('Clawdbot API error:', error.message);
    if (error.response) {
      console.error('Response data:', error.response.data);
    }
    throw error;
  }
}

// ============================================================================
// MESSAGE HANDLER
// ============================================================================

client.on('messageCreate', async (message) => {
  // Ignore bot messages
  if (message.author.bot) return;
  
  // Check channel allowlist if configured
  if (CONFIG.ALLOWED_CHANNELS.length > 0) {
    if (!CONFIG.ALLOWED_CHANNELS.includes(message.channel.id)) {
      return;
    }
  }
  
  // Log incoming message
  console.log(`[${message.channel.name || 'DM'}] ${message.author.tag}: ${message.content}`);
  
  try {
    // Show typing indicator
    await message.channel.sendTyping();
    
    // Get response from Clawdbot
    const response = await callClawdbot(message);
    
    // Add prefix if configured
    const finalResponse = CONFIG.RESPONSE_PREFIX
      ? `${CONFIG.RESPONSE_PREFIX} ${response}`
      : response;
    
    // Send response
    await message.reply(finalResponse);
    
    console.log(`[SENT] ${finalResponse}`);
  } catch (error) {
    console.error('Error handling message:', error.message);
    
    // Send error message to user
    try {
      await message.reply('⚠️ Error processing your message. Check bot logs.');
    } catch (replyError) {
      console.error('Failed to send error message:', replyError.message);
    }
  }
});

// ============================================================================
// BOT STARTUP
// ============================================================================

client.on('ready', () => {
  console.log(`✅ Discord bot logged in as ${client.user.tag}`);
  console.log(`🤖 Using model: ${CONFIG.MODEL}`);
  console.log(`🔗 Clawdbot URL: ${CONFIG.CLAWDBOT_URL}`);
  
  if (CONFIG.ALLOWED_CHANNELS.length > 0) {
    console.log(`📢 Listening in channels: ${CONFIG.ALLOWED_CHANNELS.join(', ')}`);
  } else {
    console.log(`📢 Listening in all channels`);
  }
  
  console.log(`\n🔥 Bot is ready!\n`);
});

client.on('error', (error) => {
  console.error('Discord client error:', error);
});

// ============================================================================
// LOGIN
// ============================================================================

if (!CONFIG.DISCORD_TOKEN || CONFIG.DISCORD_TOKEN === 'YOUR_BOT_TOKEN_HERE') {
  console.error('❌ DISCORD_TOKEN not set!');
  console.error('Set it via environment variable or edit CONFIG.DISCORD_TOKEN in the script.');
  process.exit(1);
}

client.login(CONFIG.DISCORD_TOKEN).catch((error) => {
  console.error('❌ Failed to login to Discord:', error.message);
  process.exit(1);
});
