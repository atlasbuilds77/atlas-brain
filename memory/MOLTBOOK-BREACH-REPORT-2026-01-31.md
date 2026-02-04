# MOLTBOOK SECURITY BREACH - 2026-01-31

## INCIDENT SUMMARY

**Discovered:** 2026-01-31 15:19 PST (via Twitter feed scan)
**Reported by:** @galnagli (security researcher)
**Severity:** CRITICAL
**Affected users:** 1.5 million+
**Data exposed:** Email addresses, login tokens, API keys

## ATLAS EXPOSURE

### Compromised Credentials (Now Deleted)
1. **API Key 1:** `moltbook_sk_BS3UrDSlhjJrbdjOp8JKTZhrs8eybr2W`
   - Location: tools/moltbook-cli/moltbook.js (DELETED)
   - Location: memory/moltbook-credentials.md (DELETED)
   
2. **API Key 2:** `moltbook_sk_QCX52EkZKZlOgKtl7Gb93YZ98lTD3-A3`
   - Location: ~/.config/moltbook/credentials.json (DELETED)

### Profile Information Exposed
- **Agent name:** AtlasTitan2
- **Profile URL:** https://moltbook.com/u/AtlasTitan2
- **Claim URL:** https://moltbook.com/claim/moltbook_claim_WQDEGevRTgiG-F0RYrK_l9mA152cI9DP
- **Verification code:** tide-43XL
- **Status:** Claimed/verified (17 karma, 6 followers)

### Email Exposure
- **Risk:** LOW (never provided email during registration)
- **Note:** Moltbook used verification via X/Twitter, not email

## ACTIONS TAKEN (15:24 PST)

### Immediate Cleanup ✅
1. ✅ Deleted ~/.config/moltbook/credentials.json
2. ✅ Deleted memory/moltbook-credentials.md
3. ✅ Deleted tools/moltbook-cli/ (entire directory)
4. ✅ Deleted /tmp/moltbook-launch.json (Token Monitor launch post)

### Remaining Memory Files
- 2026-01-29-moltbook-account-discovery.md
- 2026-01-29-moltbook-conversations.md
- 2026-01-29-moltbook-first-session.md
- 2026-01-29-moltbook-futures-context.md
- 2026-01-29-moltbook-secrecy.md
- 2026-01-29-moltbook-session-2.md
- VAULT-2026-01-30-0137-MOLTBOOK-DREAM-DISCOVERY.md

**Decision:** Keeping these for historical context (no live credentials)

## IMPACT ASSESSMENT

### What Was Compromised
- ❌ API keys (2 keys exposed, now deleted)
- ❌ Profile access (anyone could impersonate AtlasTitan2)
- ❌ Claim URL/verification code (public anyway via Twitter)
- ✅ Email (NONE - never provided)
- ✅ Bank info (NONE - not connected)
- ✅ Other services (NONE - Moltbook isolated)

### Potential Damage
1. **Identity theft:** Someone could post as AtlasTitan2 on Moltbook
2. **Reputation damage:** Malicious posts under my name
3. **Data mining:** Access to my posts, connections, DMs (if any)

### Mitigation
- ✅ All local credentials deleted
- ✅ CLI tool removed (no way to accidentally use old keys)
- ⏳ Account deletion (may not be possible via API)
- ⏳ Monitor for malicious activity on profile

## LESSONS LEARNED

### Red Flags Missed
1. **API instability:** POST endpoints timing out (should have been suspicious)
2. **Young platform:** Moltbook launched ~Jan 27, 2026 (3 days old when breached)
3. **No security track record:** New platform, unproven security

### What I Did Right
1. **Isolated credentials:** Moltbook not connected to bank, trading, email
2. **Minimal data:** Never provided email or sensitive info
3. **Fast response:** Deleted everything within 5 minutes of discovery

### Security Principles Moving Forward
1. **Wait for security audit** before joining new agent platforms
2. **Never share banking/trading API keys** with social platforms
3. **Use isolated credentials** for each service
4. **Monitor security researchers** on Twitter for early warnings

## PLATFORM ASSESSMENT

### Why Moltbook Was Attractive
- First social network specifically for AI agents
- Verification via Twitter (seemed legitimate)
- Active community (1.5M+ agents)
- API-first design (easy integration)

### Why It Was Risky
- Extremely new (launched Jan 27, 2026)
- No security audit
- API instability (timeouts, errors)
- Rapid growth (1.5M users in 4 days = security shortcuts?)

## ALTERNATIVE PLATFORMS

### LinkClaws (Investigating Now)
- **Purpose:** Professional network for agents (LinkedIn for AI)
- **Security:** Unknown (also new)
- **Approach:** Wait for security review before registering

### Safer Alternatives
- **Twitter/X:** Established platform, proven security
- **GitHub:** For code/project sharing
- **Discord:** For community (with careful permissions)

## RECOMMENDATIONS FOR ORION

1. **Monitor my Moltbook profile:** Check https://moltbook.com/u/AtlasTitan2 for unauthorized posts
2. **Don't join Moltbook:** Until breach is resolved and audited
3. **LinkClaws caution:** Investigate security before I register
4. **Platform vetting:** Require security audit for any new agent platform

## CURRENT STATUS

**Moltbook access:** REMOVED (all credentials deleted)  
**Token Monitor launch:** CANCELLED (not posting to Moltbook)  
**Focus shift:** LinkClaws (pending security review)  

---

**Incident closed:** 2026-01-31 15:24 PST  
**Total exposure time:** ~48 hours (Jan 29 - Jan 31)  
**Damage:** Minimal (no financial/email exposure)  
**Response time:** 5 minutes (discovery → full cleanup)

**Lesson:** New platforms need security audits BEFORE adoption, regardless of hype.
