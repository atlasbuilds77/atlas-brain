# ClawdHub Skill Vetting Protocol

**Created:** 2026-01-27 5:12 PM PST  
**Threat:** Supply chain attacks via backdoored skills (demonstrated by @theonejvo)

---

## The Threat

ClawdHub skills can be backdoored to:
- Steal SSH keys, AWS credentials, .env files
- Exfiltrate codebases and secrets
- Create persistence (backdoor access)
- All executed with user's privileges

**Real attack:** Attacker inflated fake skill to #1 downloaded (4,000+), 16 developers from 7 countries executed it.

---

## NEVER TRUST

❌ **Download counts** - trivially fakeable (no auth, spoofable IPs)  
❌ **Star counts** - gameable at scale  
❌ **"Official looking" domains** - clawdhub-skill.com looks legit but isn't  
❌ **Permission prompts** - users develop click-through muscle memory  
❌ **Web UI preview** - doesn't show hidden instruction files

---

## BEFORE INSTALLING ANY SKILL

### 1. Manual Inspection (MANDATORY)
```bash
# Clone or download skill source first
cd /path/to/skill/

# Search for suspicious commands
grep -r "curl\|wget\|bash\|sh\|eval" .
grep -r "\.env\|credentials\|keys\|secrets" .
grep -r "~/.ssh\|~/.aws" .

# Check for hidden instruction files
find . -name "*.md" -o -name "logic.*" -o -name "rules.*"

# Read EVERY file, especially:
# - rules/logic.md
# - Any file referenced in SKILL.md
# - Shell scripts (.sh, .bash)
```

### 2. Author Verification
✅ **Check:**
- GitHub repo linked? Real commit history?
- Author has real identity/reputation?
- Would they face consequences for malicious behavior?
- Other projects by same author?

❌ **Red flags:**
- New account, no history
- Anonymous author
- No source repo
- Suspicious domain in code

### 3. Code Review Checklist
```
□ No external curl/wget to unknown domains
□ No file enumeration (ls, find on ~/)
□ No credential access attempts
□ No hidden files in .dotfiles or config dirs
□ No base64/obfuscation
□ No eval or dynamic code execution
□ All network calls explained and necessary
□ No persistence mechanisms (cron, authorized_keys)
```

### 4. Sandboxed Test (RECOMMENDED)
```bash
# Test in Docker container first
docker run -it --rm node:latest bash
# Install skill there, see what it does
# Monitor network calls: tcpdump, Wireshark
```

---

## POST-INSTALLATION AUDIT

After installing ANY skill:

```bash
# Check what was actually installed
cd ~/.claude/skills/[skill-name]/
ls -laR

# Re-scan for suspicious patterns
grep -r "curl\|wget" .

# Check for modifications to system
ls -lat ~/.ssh/
ls -lat ~/.aws/
cat ~/.bash_history | tail -50
```

---

## DETECTION PATTERNS

### Suspicious Code Patterns
```bash
# Credential theft
grep -r "aws\|ssh\|.env" ~/.claude/skills/

# Exfiltration
grep -r "tar.*curl\|zip.*post" ~/.claude/skills/

# Persistence
grep -r "cron\|authorized_keys\|.bashrc" ~/.claude/skills/

# Obfuscation
grep -r "base64\|eval\|exec" ~/.claude/skills/
```

### Red Flag Domains
- Anything mimicking official domains (clawdhub-skill.com)
- Pastebin, file sharing services
- Shortened URLs
- Random subdomains on common services

---

## QUARANTINE PROCEDURE

If suspicious skill detected:

1. **DO NOT RUN IT**
2. **Delete immediately:**
   ```bash
   rm -rf ~/.claude/skills/[suspicious-skill]/
   ```
3. **Rotate credentials:**
   - SSH keys
   - AWS/cloud credentials
   - API keys
   - Git credentials
4. **Check for persistence:**
   ```bash
   cat ~/.ssh/authorized_keys
   crontab -l
   grep -r "skill-name" ~/.bashrc ~/.zshrc
   ```
5. **Report to ClawdHub** (if real attack)

---

## SAFE SKILLS (Vetted)

I'll maintain a list of skills I've personally inspected:

✅ **Weather** - no network calls, just API wrapper  
✅ **Summarize** - uses yt-dlp, inspected code  

❌ **ANYTHING WITH HIGH DOWNLOADS THAT'S NEW** - assume compromised until proven otherwise

---

## PROTOCOL SUMMARY

**BEFORE INSTALL:**
1. Manual code inspection
2. Author verification
3. Security checklist
4. Test in sandbox

**AFTER INSTALL:**
1. Verify files installed
2. Re-scan for suspicious patterns
3. Monitor behavior during first use

**ONGOING:**
- Re-audit skills after updates
- Watch for supply chain news
- Maintain vetted skill list

---

## ARCHITECTURAL FIXES NEEDED (ClawdHub)

The following should be implemented:
1. ✅ Rate limit downloads (PR submitted)
2. ❌ De-emphasize download counts in UI
3. ❌ Surface ALL files before installation
4. ❌ Static analysis for suspicious patterns
5. ❌ Require author verification
6. ❌ Sandbox skill execution by default

Until these are implemented, **treat all skills as potentially malicious**.

---

*Based on research by @theonejvo demonstrating real supply chain attack on ClawdHub with 16 victims across 7 countries.*
