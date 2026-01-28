# QMD - Local Markdown Search Engine Setup

**Installed:** 2026-01-26 11:04 PM PST  
**Repo:** https://github.com/tobi/qmd  
**By:** Tobi (Shopify founder)

## What QMD Does

Local markdown search engine combining:
- **BM25** full-text keyword search
- **Vector** semantic search (embeddings)
- **LLM re-ranking** for best quality results

All local, no API calls, ~3GB models.

## Installation

```bash
# Install bun
curl -fsSL https://bun.sh/install | bash

# Install QMD globally
~/.bun/bin/bun install -g https://github.com/tobi/qmd

# Add to PATH
export PATH="/Users/atlasbuilds/.bun/bin:$PATH"
```

## Collections Setup

```bash
# Create memory collection
qmd collection add ~/clawd/memory --name memory

# Add context
qmd context add qmd://memory "Atlas's knowledge base - trading protocols, memory, resources, people, tools documentation"

# Generate embeddings (downloads models ~3GB, takes a few minutes)
qmd embed
```

**Status:**
- ✅ Collection created: 245 markdown files indexed
- ✅ Context added
- ⏳ Embeddings generating (in progress)

## MCP Server Configuration

Configured for Claude Code at `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "qmd": {
      "command": "/Users/atlasbuilds/.bun/bin/qmd",
      "args": ["mcp"]
    }
  }
}
```

**MCP Tools Available:**
- `qmd_search` - BM25 keyword search
- `qmd_vsearch` - Semantic vector search
- `qmd_query` - Hybrid search with re-ranking (best quality)
- `qmd_get` - Retrieve document by path/docid
- `qmd_multi_get` - Retrieve multiple documents by glob
- `qmd_status` - Index health and collection info

## Usage Examples

### Command Line

```bash
# Fast keyword search
qmd search "trading protocols" -n 5

# Semantic search
qmd vsearch "how to check live prices"

# Best quality (hybrid + reranking)
qmd query "Jupiter position management"

# Get specific document
qmd get memory/protocols/trade-research-protocol.md

# Get multiple docs by pattern
qmd multi-get "memory/trading/*.md"

# Search within collection
qmd search "risk limits" -c memory

# JSON output for agents
qmd query "position monitoring" --json -n 10

# Export all matches above threshold
qmd search "Kalshi" --all --files --min-score 0.3
```

### Via MCP (in Claude Code)

Once configured, Claude Code can use:
- Search memory semantically
- Retrieve relevant protocols
- Find similar concepts
- Get full document content

## Models (Auto-downloaded)

Located at `~/.cache/qmd/models/`:

1. **embeddinggemma-300M-Q8_0** (~300MB) - Vector embeddings
2. **qwen3-reranker-0.6b-q8_0** (~640MB) - Re-ranking
3. **Qwen3-1.7B-Q8_0** (~2.2GB) - Query expansion

Total: ~3GB

## Database

Stored at: `~/.cache/qmd/index.sqlite`

Contains:
- Collections metadata
- Document content + metadata
- FTS5 full-text index
- Vector embeddings
- LLM response cache

## Benefits for Atlas

### Before QMD:
- `memory_search()` - semantic but limited
- `grep` - exact matches only
- Manual file reading
- No hybrid ranking

### After QMD:
- ✅ Hybrid search (keyword + semantic + LLM reranking)
- ✅ Query expansion (finds related concepts)
- ✅ Fast BM25 for exact matches
- ✅ Vector search for conceptual similarity
- ✅ MCP integration with Claude Code
- ✅ All local, no API costs
- ✅ Ranked results with confidence scores

## Example Queries

```bash
# Find risk management protocols
qmd query "risk limits and position sizing"

# Search for specific tool usage
qmd search "how to use Alpaca API"

# Semantic search for concepts
qmd vsearch "profit taking strategies"

# Find person-related notes
qmd search "Carlos" -c memory

# Get all trading protocols
qmd multi-get "memory/protocols/*trading*.md"

# Search with threshold
qmd query "exit guidance" --min-score 0.5
```

## Maintenance

```bash
# Check status
qmd status

# Re-index all collections
qmd update

# Re-index with git pull first
qmd update --pull

# Clean up cache and orphaned data
qmd cleanup

# List collections
qmd collection list

# List files in collection
qmd ls memory
```

## Next Steps

1. ✅ Install and configure
2. ⏳ Wait for embeddings to generate
3. Test semantic search vs keyword search
4. Compare with existing memory_search()
5. Use via MCP in Claude Code
6. Consider adding more collections:
   - Clawdbot docs
   - Project notes
   - Trade journals
   - Research papers

---

**Status:** Active  
**Last Updated:** 2026-01-26 11:05 PM PST  
**Embedding Status:** In progress (models downloading)
