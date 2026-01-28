# Clawdbot Session Metadata & Context Exposure Options

**Investigation Date:** 2026-01-27
**Config Version:** clawdbot@2026.1.24-3

## Summary

Session metadata **IS** exposed to agents, particularly subagents. The information appears in the system prompt under different sections depending on the agent mode. There are configuration options that control the level of detail and context visibility.

## Current Session Metadata Exposure

### What's Already Visible to Agents

#### Runtime Section (All Agents)
All agents receive a "Runtime:" line in their system prompt with:
- `agent` - Agent ID (e.g., "main", "subagent:xxx")
- `host` - Hostname
- `repo` - Repository/workspace root path
- `os` - Operating system and architecture
- `node` - Node.js version
- `model` - Current model being used
- `default_model` - Default model configuration
- `channel` - Channel name (e.g., "imessage", "telegram")
- `capabilities` - Channel capabilities list
- `thinking` - Current thinking level setting

**Location in code:** `/opt/homebrew/lib/node_modules/clawdbot/dist/agents/system-prompt.js:443`

#### Subagent Context Section (Subagents Only)
Subagents receive a dedicated "Session Context" section with:
- `Label` - Session label/description
- `Requester session` - Session key of the spawning agent
- `Requester channel` - Channel where the request originated
- `Your session` - The subagent's own session key

**Location in code:** `/opt/homebrew/lib/node_modules/clawdbot/dist/agents/subagent-announce.js:236-240`

#### Group Chat Context (Main Agents in Groups)
Main agents in group chats receive group metadata via `extraSystemPrompt` parameter.

## Configuration Options

### 1. `verboseDefault` - Agent Verbosity Level
**Path:** `agents.defaults.verboseDefault`
**Type:** `enum`
**Values:** `"off"` | `"on"` | `"full"`
**Default:** `"off"`

Controls the default verbosity level for agent operations. This affects logging and potentially context exposure.

**Schema location:** `/opt/homebrew/lib/node_modules/clawdbot/dist/config/zod-schema.agent-defaults.js:100`

**Example config:**
```json
{
  "agents": {
    "defaults": {
      "verboseDefault": "full"
    }
  }
}
```

### 2. `sessionToolsVisibility` - Sandbox Tool Visibility
**Path:** `agents.defaults.sandbox.sessionToolsVisibility`
**Type:** `enum`
**Values:** `"spawned"` | `"all"`
**Default:** `"spawned"`

Controls which session tools are visible to sandboxed agents:
- `"spawned"` - Only tools spawned by this session
- `"all"` - All session tools across the agent

**Schema location:** `/opt/homebrew/lib/node_modules/clawdbot/dist/config/zod-schema.agent-runtime.js:199`

**Example config:**
```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "sessionToolsVisibility": "all"
      }
    }
  }
}
```

### 3. `thinkingDefault` - Reasoning Detail Level
**Path:** `agents.defaults.thinkingDefault`
**Type:** `enum`
**Values:** `"off"` | `"minimal"` | `"low"` | `"medium"` | `"high"` | `"xhigh"`
**Default:** `"off"`

Controls the default reasoning/thinking level, which affects how much internal reasoning is shown.

**Schema location:** `/opt/homebrew/lib/node_modules/clawdbot/dist/config/zod-schema.agent-defaults.js:87-95`

### 4. Sandbox Context Scope
**Path:** `agents.defaults.sandbox.scope`
**Type:** `enum`
**Values:** `"session"` | `"agent"` | `"shared"`
**Default:** Not explicitly documented

Controls the scope of sandbox context isolation.

**Schema location:** `/opt/homebrew/lib/node_modules/clawdbot/dist/config/zod-schema.agent-runtime.js:200`

## Channel Plugin Metadata Options

Channel plugins expose metadata differently. Based on the config schema inspection:

### iMessage Plugin
- `includeAttachments` - Controls attachment visibility (boolean)
- Groups have explicit IDs in config

### Telegram Plugin
- `streamMode` - Controls how messages are streamed ("partial" or others)
- Reaction actions configurable

### Channel-Agnostic Settings
**Path:** `channels.[channelName].metadata.*` - Not found as a top-level option

## Findings & Recommendations

### What We Can't Currently Control via Config

Based on schema inspection, there is **NO** direct config flag like:
- `exposeSessionMetadata: true/false`
- `showSessionId: true/false`
- `sessionMetadataVerbosity: "minimal" | "full"`
- `includeOriginMetadata: true/false`

### What IS Controllable

1. **Verbosity level** - `verboseDefault` can be set to "full" for more detailed output
2. **Sandbox isolation** - `sessionToolsVisibility` and `scope` control context boundaries
3. **Thinking output** - `thinkingDefault` controls reasoning visibility
4. **Subagent context** - Always includes session metadata by design (not configurable)

### Current Implementation

The session metadata exposure is **hardcoded** in the system prompt building logic:
- Main agents get runtime info
- Subagents get enhanced session context
- Group chats get group metadata

**There is no config switch to expand or suppress this information.**

## Workaround: Inject Custom Metadata

To expose additional metadata to agents, you can:

1. **Use `extraSystemPrompt` parameter** (programmatic)
2. **Add to workspace context files** (AGENTS.md, IDENTITY.md, etc.)
3. **Modify channel plugin** to inject custom context

## Schema File Locations

Key schema files examined:
- `zod-schema.agents.js` - Top-level agent schema
- `zod-schema.agent-defaults.js` - Default agent settings
- `zod-schema.agent-runtime.js` - Runtime agent configuration
- `zod-schema.channels.js` - Channel plugin configuration
- `system-prompt.js` - System prompt builder (contains hardcoded metadata)
- `subagent-announce.js` - Subagent context builder

## Related Config Paths

```
agents.defaults.verboseDefault           # Verbosity level
agents.defaults.thinkingDefault          # Reasoning detail
agents.defaults.sandbox.sessionToolsVisibility  # Tool scope
agents.defaults.sandbox.scope            # Context isolation
agents.defaults.contextTokens            # Token budget
agents.defaults.contextPruning.mode      # Context management
channels.[name].includeAttachments       # Channel-specific
```

## Testing Notes

To test metadata visibility:
1. Set `verboseDefault: "full"` in config
2. Spawn a subagent and check its "Session Context" section
3. Check main agent's "Runtime:" line for current info
4. Compare output with different `sessionToolsVisibility` settings

## Conclusion

**Answer to the main question: Can we flip a switch to make metadata visible?**

**Partially YES for subagents** - They already receive enhanced session metadata automatically.

**NO for main agents** - There is no config flag to expose more session metadata. The Runtime line is the extent of what's shown. To add more metadata to main agents, you would need to:
1. Modify the source code in `system-prompt.js`
2. Use workspace context files (AGENTS.md, etc.)
3. Inject via extraSystemPrompt parameter programmatically

**Best current option:** Use `verboseDefault: "full"` for more detailed logging, but this doesn't directly expose more session metadata in the agent's context.
