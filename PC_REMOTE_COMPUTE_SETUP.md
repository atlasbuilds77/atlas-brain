# PC Remote Compute Setup (48GB RAM)

Use Orion's PC as heavy compute node for local LLMs.

## PC Specs
- 48GB RAM (way more than Mac Mini)
- Sits idle most of the time
- Can run 70B models easily

## Setup (Do After Mac Mini is Running)

### On Orion's PC (Windows)

1. **Install Ollama:**
   - Download: https://ollama.com/download/windows
   - Install and run
   - Test: `ollama run llama3.2`

2. **Enable SSH (Optional but Recommended):**
   - Settings → Apps → Optional Features → OpenSSH Server
   - Services → OpenSSH Server → Start → Set to Automatic

3. **Get PC IP Address:**
   ```cmd
   ipconfig
   ```
   Note the IPv4 address (e.g., 192.168.1.100)

4. **Configure Firewall:**
   - Allow Ollama (port 11434)
   - Allow SSH (port 22) if enabled

### On Mac Mini (Atlas)

1. **Test Connection:**
   ```bash
   # If SSH enabled:
   ssh orion@[PC-IP]
   
   # Or just test Ollama API:
   curl http://[PC-IP]:11434/api/tags
   ```

2. **Create Helper Script:**
   ```bash
   # ~/clawd/scripts/use-pc-llm.sh
   #!/bin/bash
   OLLAMA_HOST=http://[PC-IP]:11434 ollama run $1
   ```

3. **Usage:**
   ```bash
   # From Mac Mini, use PC's Ollama:
   OLLAMA_HOST=http://192.168.1.100:11434 ollama run llama3.1:70b
   ```

## What This Enables

**Can run on PC (via Mac Mini control):**
- Llama 3.1 70B (way smarter than small models)
- Qwen 72B
- Custom fine-tuned models
- Code generation (DeepSeek Coder)
- Long context tasks (100k+ tokens)

**Use cases:**
- Complex analysis when API isn't needed
- Experimentation with models
- Custom training/fine-tuning
- Cost-free LLM tasks

## Architecture

```
Mac Mini (16GB)          Orion's PC (48GB)
─────────────────        ─────────────────
│               │        │                │
│  Clawdbot     │───────▶│  Ollama        │
│  Orchestrator │  SSH   │  Heavy Compute │
│  Always-On    │  HTTP  │  On-Demand     │
│               │        │                │
─────────────────        ─────────────────
```

**Mac Mini:** Brain, coordination, always-on
**PC:** Muscle, heavy compute, as-needed

## Models to Install on PC

Start with these:
```bash
ollama pull llama3.1:70b        # General intelligence
ollama pull qwen2.5:72b         # Coding/reasoning
ollama pull deepseek-coder:33b  # Code generation
```

## Cost Savings

**API costs for 70B-equivalent:**
- Claude Opus: ~$15/M tokens
- GPT-4: ~$30/M tokens

**PC with Ollama:**
- $0 (just electricity)
- Unlimited usage

**When to use PC vs API:**
- PC: Experimentation, bulk tasks, learning
- API: Critical tasks, need best quality, time-sensitive

## Maintenance

**PC side:**
- Keep Ollama updated
- Monitor disk space (models are large)
- PC can sleep when not in use (I wake it via network)

**Mac Mini side:**
- Save PC IP in config
- Create convenience aliases
- Monitor connection

## Future: GPU Addition (Optional)

If you add GPU to PC later:
- RTX 4090 → Way faster inference
- Can run even bigger models
- Ollama automatically uses GPU

But 48GB RAM alone is already huge.

---

**Status:** Not set up yet
**Priority:** Medium (after Mac Mini is stable)
**Time to set up:** ~15 minutes
