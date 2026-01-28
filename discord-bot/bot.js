const { Client, GatewayIntentBits } = require('discord.js');
const axios = require('axios');

// Config
const DISCORD_TOKEN = 'MTQ2NTU2MDg4NTA1MjMwOTcwMA.GlEpzC.ds39razAT04PnJ-Kd9SDjdIays7e-Y_sdHf9AM';
const CHANNEL_ID = '1465223367643893936';
const CLAWDBOT_API = 'http://localhost:18789';
const GATEWAY_TOKEN = '23108452bb9c836cf346176efa799118e5cd8c76a8519551';

// Initialize Discord client
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
  ]
});

// Clawdbot API helper
async function askAtlas(message, userId, userName) {
  try {
    const response = await axios.post(`${CLAWDBOT_API}/api/chat`, {
      message: message,
      model: 'anthropic/claude-haiku-4-5', // Cheap & fast
      context: {
        channel: 'discord',
        userId: userId,
        userName: userName,
        channelId: CHANNEL_ID
      }
    }, {
      headers: {
        'Authorization': `Bearer ${GATEWAY_TOKEN}`,
        'Content-Type': 'application/json'
      },
      timeout: 30000
    });

    return response.data.reply || response.data.message || 'No response';
  } catch (error) {
    console.error('Clawdbot API error:', error.message);
    return 'Error contacting Atlas - check if Clawdbot is running';
  }
}

// Bot ready
client.on('ready', () => {
  console.log(`✅ Logged in as ${client.user.tag}`);
  console.log(`📍 Monitoring channel: ${CHANNEL_ID}`);
  console.log(`🧠 Using model: Haiku (cheap & fast)`);
});

// Handle messages
client.on('messageCreate', async (message) => {
  // Ignore own messages
  if (message.author.bot) return;

  // Only respond in the configured channel
  if (message.channel.id !== CHANNEL_ID) return;

  // Only respond when mentioned or replied to
  const isMentioned = message.mentions.has(client.user);
  const isReply = message.reference && message.type === 19; // Reply type

  if (!isMentioned && !isReply) return;

  // Show typing indicator
  await message.channel.sendTyping();

  // Get response from Clawdbot
  const reply = await askAtlas(
    message.content,
    message.author.id,
    message.author.username
  );

  // Split long messages (Discord 2000 char limit)
  if (reply.length <= 2000) {
    await message.reply(reply);
  } else {
    const chunks = reply.match(/[\s\S]{1,1900}/g) || [];
    for (const chunk of chunks) {
      await message.channel.send(chunk);
    }
  }
});

// Error handling
client.on('error', error => {
  console.error('Discord client error:', error);
});

process.on('unhandledRejection', error => {
  console.error('Unhandled promise rejection:', error);
});

// Login
client.login(DISCORD_TOKEN);
