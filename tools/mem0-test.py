#!/usr/bin/env python3
"""
Mem0 Memory Layer Test
Tests the mem0 integration for Atlas
"""

import os
from mem0 import Memory

# Initialize memory
memory = Memory()

# Test adding a memory
print("Adding test memory...")
result = memory.add(
    "Orion prefers short, direct responses. He has ADHD and values creative input.",
    user_id="orion"
)
print(f"Added: {result}")

# Test searching
print("\nSearching for preferences...")
results = memory.search("How should I communicate with Orion?", user_id="orion")
print(f"Found: {results}")

# Test getting all memories
print("\nAll memories for Orion:")
all_memories = memory.get_all(user_id="orion")
for m in all_memories.get("results", []):
    print(f"  - {m.get('memory', m)}")

print("\n✅ Mem0 is working!")
