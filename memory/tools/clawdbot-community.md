# Clawdbot Community Research

## Date: 2026-01-24

---

## COOLEST SETUP FOUND: Henry's "Enterprise Crew"

Source: https://medium.com/@henrymascot/my-almost-agi-with-clawdbot-cd612366898b

### Architecture
- **3 AI agents across 3 machines** (2 GCP VMs + 1 Raspberry Pi)
- Agents can **SSH into each other's machines and debug each other**
- Example: Asked Scotty "what's wrong with Ada?" → He SSH'd in, found bloated context, fixed and restarted her

### Daily Automations
- 7am: Automated brief (emails + slack + calendar) → Obsidian vault + **ElevenLabs voice summary**
- Proactive alerts for Slack mentions and urgent emails
- Fireflies transcripts → auto-synced, action items extracted
- Discord #showcase posts curated automatically
- Daily performance review (screen time, meetings, code written)
- 40 custom skills built by conversation
- Smart home control via text

### Agent Specialization
- **Ada (Opus 4.5)** - Main agent, delegates work
- **Spock (Sonnet/Gemini)** - Research
- **Scotty (Codex 5.2)** - Building/coding
- They ping each other when done. No manual handoffs.

### Cost
- AI Inference: ~$300/month (Opus, Codex, MiniMax, Gemini)
- Infrastructure: $50/mo GCP + $120 Raspberry Pi (one-time)

### Key Insight
"We are not just in the era of personal Assistants, but era of agent teams."

---

## OTHER COMMUNITY PROJECTS

### WhatsApp Memory Vault
- Connected startup's entire WhatsApp history (1000+ voice messages)
- Clawdbot transcribed them
- Cross-referenced with Git commits
- Generated searchable knowledge base

### Grocery Autopilot
- Photo of recipe → extract ingredients → map to grocery store → add to online cart
- Idea to shopping cart in under 5 minutes

---

## CLAWDHUB POPULAR SKILLS

From https://clawdhub.com/skills:
- Web research / summarization
- Browser automation (headless Chrome)
- Email and calendar (Gmail, Google Calendar)
- Developer tools (run commands, check logs)
- Meeting notes integration (Fireflies)
- Google Workspace (gog skill)
- GitHub integration

---

## REDDIT INSIGHTS (r/LocalLLaMA, r/selfhosted)

### Use Cases
- DevOps workflow (Claude Code style from anywhere)
- "Agentic version of Home Assistant"
- Unified interface across all devices
- Local-first, data control

### Token Warning
"Token usage is kind of insane. Can max out a 5 hour window of $200 Claude plan in an hour" (for heavy dev work)

### Local Model Support
- People switching from Opus to OSS models (120B, Qwen3 80B)
- Testing phase ongoing

---

## COMMUNITY STATS

- Discord: 0 → 5000 members in 2 weeks (predicted 10k by month end)
- Very active - bugs fixed while you're still reporting them
- Two Clawdbot instances answering questions in Discord

---

## IDEAS FOR US

### Short Term
1. **Voice briefings via ElevenLabs** - Morning summary read aloud
2. **Multi-agent setup** - Spawn sub-agents for specialized tasks
3. **SSH between machines** - If we set up Orion's PC, agents could coordinate
4. **Obsidian integration** - Save important context to vault

### Medium Term
1. **Agent specialization** - One for trading, one for coding, one for research
2. **Cross-agent debugging** - Agents fix each other
3. **Fireflies/meeting integration** - Auto action items

### Long Term
1. **Full "Enterprise Crew"** - Multiple specialized agents
2. **Home automation via text** - Smart home control
3. **Daily performance metrics** - Track output automatically

---

## RESOURCES

- Discord: https://discord.com/invite/clawd
- ClawdHub: https://clawdhub.com/skills
- GitHub: https://github.com/clawdbot/clawdbot
- Docs: https://docs.clawd.bot

---

*This is what's possible. We're just getting started.*
