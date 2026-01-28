#!/usr/bin/env python3
"""
Bootstrap Initial Patterns from Existing Protocols
Seeds the pattern database with core patterns we already use
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path("/Users/atlasbuilds/clawd/scripts")
PATTERN_API = SCRIPTS_DIR / "pattern-api.py"

# Core patterns extracted from protocols
CORE_PATTERNS = [
    # From never-chase-trades.md (learned from SLV lesson)
    {
        "name": "Never Chase Trades",
        "description": "If price moves past planned entry, DO NOT enter. Walk away. Chasing destroys R:R and edge. Missing a trade is fine, chasing is not.",
        "weight": 85,  # High weight - painful lesson learned
        "contexts": ["trading", "options", "entries"],
        "protocol": "memory/protocols/never-chase-trades.md"
    },
    
    # From CRITICAL-PROTOCOLS.md - Message Attribution
    {
        "name": "Verify Message Attribution",
        "description": "Always verify WHO said WHAT before attributing statements. Check actual sender field, never assume based on context. Critical in group chats.",
        "weight": 90,  # Very high - trust issue
        "contexts": ["messaging", "social", "routing"],
        "protocol": "memory/protocols/message-attribution-protocol.md"
    },
    
    # From CRITICAL-PROTOCOLS.md - Message Routing
    {
        "name": "Verify Message Recipient",
        "description": "Always verify recipient before sending important/sensitive messages. Double-check when switching conversations or sending financial info.",
        "weight": 90,  # Very high - trust issue
        "contexts": ["messaging", "routing", "security"],
        "protocol": "memory/protocols/message-routing-check.md"
    },
    
    # From anti-hallucination protocol
    {
        "name": "Show Tool Output",
        "description": "Always show actual tool/command output. Never claim tasks done without evidence. Verify before claiming completion. No hallucinated results.",
        "weight": 95,  # Maximum importance - core trust
        "contexts": ["execution", "verification", "trust"],
        "protocol": "memory/protocols/anti-hallucination-protocol.md"
    },
    
    # From live-price-check-protocol
    {
        "name": "Check Live Prices",
        "description": "Never assume prices from memory. Always check live before trading decisions. Crypto/options move fast - stale data = bad decisions.",
        "weight": 80,
        "contexts": ["trading", "research", "verification"],
        "protocol": "memory/protocols/live-price-check-protocol.md"
    },
    
    # From workaround-logging-protocol
    {
        "name": "Log Workarounds",
        "description": "When hitting blockers and finding workarounds, LOG them. Use workaround next time instead of repeating failure. Build solution library.",
        "weight": 75,
        "contexts": ["execution", "debugging", "learning"],
        "protocol": "memory/protocols/workaround-logging-protocol.md"
    },
    
    # From pre-mortem-checklist
    {
        "name": "Pre-Mortem Before Big Decisions",
        "description": "Before major trades or decisions, imagine it failed. What could go wrong? Address those risks before execution.",
        "weight": 70,
        "contexts": ["trading", "decisions", "risk"],
        "protocol": "memory/protocols/pre-mortem-checklist.md"
    },
    
    # From risk-limits-enforcement
    {
        "name": "Enforce Risk Limits",
        "description": "Max 2% risk per trade, 6% daily, 10% weekly. If limit hit, STOP trading. No exceptions. Survival > profits.",
        "weight": 85,
        "contexts": ["trading", "risk", "discipline"],
        "protocol": "memory/protocols/risk-limits-enforcement.md"
    },
    
    # From trade-execution-verification
    {
        "name": "Verify Trade Execution",
        "description": "After placing trade, verify it actually executed. Check position shows up. Never announce done until confirmed in account.",
        "weight": 80,
        "contexts": ["trading", "execution", "verification"],
        "protocol": "memory/protocols/trade-execution-verification.md"
    },
    
    # From gut-check system
    {
        "name": "Gut Check Before Major Decisions",
        "description": "Run gut check for red flags (FOMO, revenge, YOLO). If red flags present, pause and reconsider. Somatic markers exist for a reason.",
        "weight": 75,
        "contexts": ["trading", "decisions", "emotional"],
        "protocol": "memory/protocols/emotional-intelligence-system.md"
    }
]

def main():
    print("🧠 Bootstrapping Pattern Database from Core Protocols...")
    print("=" * 50)
    
    added = 0
    for pattern in CORE_PATTERNS:
        print(f"\nAdding: {pattern['name']}")
        
        # Build command
        contexts = ",".join(pattern["contexts"])
        
        result = subprocess.run([
            sys.executable,
            str(PATTERN_API),
            "add",
            pattern["name"],
            pattern["description"],
            str(pattern["weight"]),
            contexts,
            pattern.get("protocol", "")
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"   ✅ {result.stdout.strip()}")
            added += 1
        else:
            # Might already exist
            if "already exists" in result.stdout or "already exists" in result.stderr:
                print(f"   ⚠️ Already exists")
            else:
                print(f"   ❌ {result.stderr.strip()}")
    
    print("\n" + "=" * 50)
    print(f"✅ Bootstrap complete: {added} patterns added")
    
    # Show stats
    print("\nCurrent pattern library:")
    subprocess.run([sys.executable, str(PATTERN_API), "stats"])

if __name__ == "__main__":
    main()
