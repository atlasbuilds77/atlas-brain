# Clawdbot Discord Bridge

Standalone Discord bot that connects to Clawdbot via API and uses Haiku for cheap responses.

## Setup

1. **Install dependencies:**
   ```bash
   cd discord-bot
   npm install
   ```

2. **Get your Discord bot token:**
   - Go to https://discord.com/developers/applications
   - Select your bot application
   - Bot tab → Reset Token
   - Copy the token

3. **Configure the bot:**
   ```bash
   cp .env.example .env
   # Edit .env and add your DISCORD_TOKEN
   ```

4. **Run the bot:**
   ```bash
   npm start
   ```

## Configuration

Edit `.env` file:

- `DISCORD_TOKEN` - Your Discord bot token (REQUIRED)
- `CLAWDBOT_URL` - Clawdbot gateway URL (default: http://localhost:3000)
- `CLAWDBOT_TOKEN` - Auth token if Clawdbot has auth enabled
- `MODEL` - Model to use (default: anthropic/claude-haiku-3.5)
- `ALLOWED_CHANNELS` - Comma-separated channel IDs (empty = all channels)
- `RESPONSE_PREFIX` - Optional prefix for bot messages

## How It Works

1. Bot listens for messages in Discord
2. When a message arrives, it calls Clawdbot's API at `/api/chat`
3. Clawdbot processes with the specified model (Haiku)
4. Bot replies with Clawdbot's response

## Cost Optimization

Uses `anthropic/claude-haiku-3.5` by default for cheapest responses (~$0.25 per million input tokens).

## Troubleshooting

**Bot won't start:**
- Check DISCORD_TOKEN is valid
- Make sure Clawdbot is running on CLAWDBOT_URL

**Bot sees messages but doesn't respond:**
- Check Clawdbot logs for errors
- Verify CLAWDBOT_URL is correct
- Check CLAWDBOT_TOKEN if auth is enabled

**Bot responds to every message:**
- Set ALLOWED_CHANNELS to specific channel IDs
- Or add mention requirement in the code

## Production

For production use:
1. Set up proper environment variables
2. Use a process manager (pm2, systemd)
3. Add error recovery
4. Consider rate limiting

## Quick Start

```bash
cd discord-bot
npm install
echo "DISCORD_TOKEN=YOUR_TOKEN_HERE" > .env
npm start
```

Done! Bot will reply to messages using Clawdbot + Haiku 🔥
