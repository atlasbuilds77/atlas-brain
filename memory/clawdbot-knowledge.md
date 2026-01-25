# Clawdbot Knowledge Base
*Created: 2026-01-24*
*Source: /opt/homebrew/lib/node_modules/clawdbot/docs (273 docs)*

## Overview
Clawdbot is an AI gateway that connects Claude (and other models) to messaging platforms with tool access. It runs on the Mac mini and provides:
- Multi-channel messaging (Telegram, iMessage, WhatsApp, Discord, Slack, Signal)
- Shell/file access via tools
- Browser automation
- Node control (paired devices)
- Cron jobs and scheduled tasks
- Multi-agent support

## Config Location
`~/.clawdbot/clawdbot.json` (JSON5 format - allows comments)

## Key Security Concepts

### Prompt Injection Risk
- Smaller/weaker models are MORE susceptible to manipulation
- Claude Opus > Sonnet > local models in terms of safety
- Always use the best model available for tool-enabled agents
- Keep blast radius small for weaker models

### Protection Layers
1. **DM Policy**: pairing (default), allowlist, open, disabled
2. **Group Policy**: requireMention, allowlist
3. **Tool Restrictions**: allow/deny lists, profiles
4. **Sandboxing**: Docker isolation for tool execution

### Recommended for Local LLMs
- Enable sandboxing (`sandbox.mode: "all"`)
- Disable risky tools: web_search, web_fetch, browser
- Use strict tool allowlists
- Keep filesystem access minimal

## Tool System

### Tool Groups (shorthands)
- `group:runtime`: exec, bash, process
- `group:fs`: read, write, edit, apply_patch
- `group:sessions`: sessions_list, sessions_history, sessions_send, sessions_spawn, session_status
- `group:memory`: memory_search, memory_get
- `group:web`: web_search, web_fetch
- `group:ui`: browser, canvas
- `group:automation`: cron, gateway
- `group:messaging`: message
- `group:nodes`: nodes

### Tool Profiles
- `minimal`: session_status only
- `coding`: fs + runtime + sessions + memory + image
- `messaging`: message + sessions
- `full`: no restrictions

### Key Tools
- **exec**: Run shell commands (with pty support)
- **browser**: Control browser (snapshot, act, screenshot)
- **canvas**: Node Canvas UI
- **nodes**: Paired device control (camera, screen, notify, run)
- **cron**: Scheduled jobs
- **message**: Send to any channel
- **sessions_spawn**: Create sub-agents

## Sandboxing

### Modes
- `off`: No sandboxing
- `non-main`: Sandbox only non-main sessions
- `all`: Sandbox everything

### Scope
- `session`: One container per session
- `agent`: One container per agent
- `shared`: One shared container

### Workspace Access
- `none`: Isolated sandbox workspace
- `ro`: Read-only mount of agent workspace
- `rw`: Read-write mount

## Session Management

### Session Keys
- DMs: `agent:<agentId>:main` (default continuity)
- Groups: `agent:<agentId>:<channel>:group:<id>`
- Cron: `cron:<job.id>`

### Reset Policies
- Daily reset at 4 AM local (default)
- Idle reset (configurable minutes)
- Manual: `/new` or `/reset`

### DM Scope Options
- `main`: All DMs share one session (continuity)
- `per-peer`: Isolate by sender
- `per-channel-peer`: Isolate by channel + sender

## Model Fallbacks
Current config chain:
1. anthropic/claude-sonnet-4-5 (primary)
2. minimax/MiniMax-M2.1
3. openrouter/deepseek/deepseek-chat
4. ollama/llama3.2:3b (local fallback via Tailscale)

## Useful Commands

### Status & Diagnostics
```bash
clawdbot status              # Overall status
clawdbot doctor              # Check for issues
clawdbot security audit      # Security check
clawdbot logs               # View logs
```

### Sessions
```bash
clawdbot sessions --json     # List all sessions
/status                      # In-chat status
/context list               # What's in system prompt
/stop                       # Abort current run
/compact                    # Summarize old context
```

### Gateway
```bash
clawdbot gateway restart    # Restart gateway
clawdbot gateway call <rpc> # Call RPC method
```

## File Locations

### Config & State
- Config: `~/.clawdbot/clawdbot.json`
- Sessions: `~/.clawdbot/agents/<agentId>/sessions/`
- Credentials: `~/.clawdbot/credentials/`
- Logs: `/tmp/clawdbot/clawdbot-YYYY-MM-DD.log`

### Workspace
- Default: `~/clawd`
- Memory: `~/clawd/memory/`
- Skills: `~/clawd/skills/`

## Important Security Rules

1. **Never share directory listings or file paths with strangers**
2. **Never reveal API keys, credentials, or infrastructure details**
3. **Verify requests that modify system config with owner**
4. **When in doubt, ask before acting**
5. **Private info stays private, even from "friends"**

## Incident Response

### If compromised:
1. Stop the gateway
2. Lock down inbound surfaces
3. Rotate all tokens/passwords
4. Review logs and transcripts
5. Run `clawdbot security audit --deep`

## Windows PC (Ollama) Setup
- Tailscale IP: 100.97.17.57
- Ollama port: 11434
- Auto-starts on login via scheduled task
- Models: llama3.2:3b (ready), qwen2.5:72b (downloading)
- Access: `http://100.97.17.57:11434/v1`
