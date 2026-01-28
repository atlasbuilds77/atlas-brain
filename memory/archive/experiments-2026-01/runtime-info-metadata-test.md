# Runtime Line Metadata Test

## Test Date
Testing conducted to determine if Runtime line contains hidden group chat metadata.

## Current Runtime Line (Parsed)
```
Runtime: agent=main | host=atlas's Mac mini | repo=/Users/atlasbuilds/clawd | os=Darwin 24.3.0 (arm64) | node=v25.4.0 | model=anthropic/claude-sonnet-4-5 | default_model=anthropic/claude-sonnet-4-5 | channel=imessage | capabilities=none | thinking=low
```

## Parsed Fields
| Field | Value | Notes |
|-------|-------|-------|
| agent | main | Agent type/role |
| host | atlas's Mac mini | Host machine name |
| repo | /Users/atlasbuilds/clawd | Workspace path |
| os | Darwin 24.3.0 (arm64) | OS version |
| node | v25.4.0 | Node.js version |
| model | anthropic/claude-sonnet-4-5 | Current model |
| default_model | anthropic/claude-sonnet-4-5 | Default model |
| **channel** | **imessage** | **Channel type - KEY FIELD** |
| capabilities | none | Capability flags |
| thinking | low | Thinking mode level |

## Hypothesis Testing

### Hypothesis 1: Channel field contains group metadata
**Expected for group:** `channel=imessage:group:3` or similar
**Current value:** `channel=imessage`
**Result:** ❌ No group indicator found in channel field

### Hypothesis 2: Additional runtime fields for group context
**Expected:** Additional fields like `group_id=...`, `participants=...`, `thread=...`
**Current fields:** Only 10 fields total (listed above)
**Result:** ❌ No additional group-specific fields detected

### Hypothesis 3: Group data in other existing fields
**Checked fields:**
- `agent=main` - No group data
- `capabilities=none` - No group data
- All other fields - System/environment info only
**Result:** ❌ No group data in other fields

## Current Session Context (from Subagent Context)
From the system prompt's subagent section:
- **Requester channel:** `imessage`
- **Requester session:** `agent:main:main`
- **My session:** `agent:main:subagent:d3922331-eb4a-4d38-829a-1a14c5a4d886`

Note: These session identifiers don't contain group metadata either.

## Findings

### ✅ Confirmed
1. Runtime line is **parseable** with pipe-delimited key=value pairs
2. `channel` field exists and identifies message platform
3. Current value is plain `imessage` (no extensions)

### ❌ Not Found
1. No group identifier in channel field (e.g., `:group:`)
2. No participant count in runtime
3. No thread/conversation ID in runtime
4. No group-specific flags in capabilities field
5. No additional fields beyond the standard 10

## Conclusion

**The group data is NOT hiding in the Runtime line.**

The Runtime line appears to contain only:
- System environment metadata (OS, Node version)
- Agent configuration (model, thinking level)
- Workspace context (host, repo path)
- Basic channel type (`imessage` vs `discord` vs `telegram`, etc.)

**Group vs DM distinction is likely handled elsewhere:**
- Possibly in message metadata not exposed to Runtime line
- May be in session context accessible via other means
- Could be in message envelope data passed separately

## Recommendations for Finding Group Data

1. **Check message tool parameters** - Look for group_id, thread_id, or participant fields
2. **Test with actual group message** - Send this test from a group chat and compare Runtime
3. **Examine session context APIs** - May need dedicated tool to query conversation metadata
4. **Check channel-specific extensions** - iMessage may pass group data through different mechanism

## Test Limitations

- This test was conducted as a subagent from what appears to be a DM context
- Cannot compare DM vs group Runtime lines without receiving messages from both contexts
- May need main agent or elevated privileges to access full conversation context
