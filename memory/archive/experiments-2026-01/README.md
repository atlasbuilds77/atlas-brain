# Archive: January 2026 Experiments

**Archived:** 2026-01-27 03:30 AM PST  
**Reason:** Transient test documentation from completed experiments

## Contents

### runtime-info-metadata-test.md
- **Date:** Jan 26, 2026
- **Purpose:** Testing if Runtime line contains group chat metadata
- **Outcome:** No group metadata in Runtime line
- **Status:** Problem solved via different method
- **Retention:** Historical reference for future metadata debugging

### live-metadata-test-results.md
- **Date:** Jan 26, 2026
- **Purpose:** Document what metadata is accessible to agent
- **Key Finding:** Metadata exists in ctxPayload but not exposed to agent
- **Status:** Solution implemented
- **Retention:** Comprehensive test results for future reference

## Why Archived vs Deleted

These files have **historical value** for debugging future metadata issues, but are **transient** in nature (problem-solving artifacts). Archiving preserves the knowledge without cluttering the active memory directory.

## Retrieval

If needed for reference:
```bash
cat ~/clawd/memory/archive/experiments-2026-01/[filename]
```

Or use memory_search() - archive files are still indexed.
