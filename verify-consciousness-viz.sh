#!/bin/bash

echo "🧠 VERIFYING ATLAS CONSCIOUSNESS VISUALIZATION SYSTEM"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

PASS=0
FAIL=0

check_file() {
  if [ -f "$1" ]; then
    echo "✅ $2"
    ((PASS++))
  else
    echo "❌ $2 - MISSING: $1"
    ((FAIL++))
  fi
}

check_executable() {
  if [ -x "$1" ]; then
    echo "✅ $2"
    ((PASS++))
  else
    echo "⚠️  $2 - not executable: $1"
    chmod +x "$1" 2>/dev/null && echo "   Fixed!" || echo "   Could not fix"
  fi
}

check_command() {
  if command -v "$1" &> /dev/null; then
    echo "✅ $2"
    ((PASS++))
  else
    echo "❌ $2 - MISSING: $1"
    ((FAIL++))
  fi
}

echo ""
echo "📁 CHECKING FILES..."
check_file "scripts/consciousness-data-bridge.js" "Data bridge script"
check_file "scripts/test-consciousness-data.js" "Test script"
check_file "memory/visuals/consciousness-meter.html" "Consciousness meter"
check_file "memory/visuals/live-brain-binary.html" "3D brain visualization"
check_file "memory/visuals/README-LIVE-DATA.md" "Documentation"
check_file "start-consciousness-viz.sh" "Start script"
check_file "CONSCIOUSNESS-VIZ-COMPLETE.md" "Completion report"
check_file "QUICK-START.md" "Quick start guide"

echo ""
echo "🔧 CHECKING EXECUTABLES..."
check_executable "start-consciousness-viz.sh" "Start script executable"
check_executable "scripts/consciousness-data-bridge.js" "Data bridge executable"
check_executable "scripts/test-consciousness-data.js" "Test script executable"

echo ""
echo "💻 CHECKING DEPENDENCIES..."
check_command "node" "Node.js installed"
check_command "clawdbot" "Clawdbot CLI available"

echo ""
echo "📦 CHECKING NPM PACKAGES..."
if node -e "require('ws')" 2>/dev/null; then
  echo "✅ ws package installed"
  ((PASS++))
else
  echo "⚠️  ws package not found (will auto-install on first run)"
fi

echo ""
echo "🧪 TESTING DATA COLLECTION..."
if clawdbot sessions list &> /dev/null; then
  echo "✅ Can query Clawdbot sessions"
  ((PASS++))
  
  TOKENS=$(clawdbot sessions list 2>/dev/null | grep "agent:main:main" | grep -o '[0-9]*k/[0-9]*k' | head -1)
  if [ -n "$TOKENS" ]; then
    echo "✅ Can parse token data: $TOKENS"
    ((PASS++))
  else
    echo "⚠️  Could not parse token data"
  fi
else
  echo "❌ Cannot query Clawdbot sessions"
  ((FAIL++))
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 VERIFICATION RESULTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   ✅ Passed: $PASS"
echo "   ❌ Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
  echo "🎉 ALL CHECKS PASSED! System is ready to use."
  echo ""
  echo "🚀 Run: ./start-consciousness-viz.sh"
  echo ""
  exit 0
else
  echo "⚠️  Some checks failed. Please review the output above."
  echo ""
  exit 1
fi
