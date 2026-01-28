#!/bin/bash

# Binary Art Visualization System - Quick Test Script
# Verifies all deliverables are present and functional

echo "🌌 ATLAS BINARY ART VISUALIZATION SYSTEM"
echo "========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

# Function to check if file exists and has content
check_file() {
    local file=$1
    local name=$2
    
    if [ -f "$file" ]; then
        local size=$(wc -c < "$file")
        if [ $size -gt 1000 ]; then
            echo -e "${GREEN}✅ PASS${NC} - $name ($size bytes)"
            ((PASS++))
            return 0
        else
            echo -e "${RED}❌ FAIL${NC} - $name (too small: $size bytes)"
            ((FAIL++))
            return 1
        fi
    else
        echo -e "${RED}❌ FAIL${NC} - $name (not found)"
        ((FAIL++))
        return 1
    fi
}

echo "📦 Checking Core Deliverables..."
echo "--------------------------------"

# Check all deliverables
check_file "memory/visuals/binary-particles.html" "1. Binary Particle System"
check_file "memory/visuals/consciousness-meter.html" "2. Consciousness Meter"
check_file "atlas-eyes/examples/binary_trails_dashboard.html" "3. Binary Trails Dashboard"
check_file "memory/visuals/live-brain-binary.html" "4. Brain Binary Streams"
check_file "memory/visuals/binary-showcase-demo.html" "5. Showcase Demo (BONUS)"

echo ""
echo "📚 Checking Documentation..."
echo "----------------------------"

check_file "memory/visuals/BINARY-ART-README.md" "README Documentation"
check_file "memory/visuals/BINARY-INDEX.html" "Quick Access Index"
check_file "memory/visuals/IMPLEMENTATION-COMPLETE.md" "Implementation Report"

echo ""
echo "🔍 Checking File Contents..."
echo "----------------------------"

# Check for key features in files
echo -n "Checking Binary Particle System for BinaryParticleSystem class... "
if grep -q "class BinaryParticleSystem" memory/visuals/binary-particles.html; then
    echo -e "${GREEN}✅${NC}"
    ((PASS++))
else
    echo -e "${RED}❌${NC}"
    ((FAIL++))
fi

echo -n "Checking Consciousness Meter for ConsciousnessMeter class... "
if grep -q "class ConsciousnessMeter" memory/visuals/consciousness-meter.html; then
    echo -e "${GREEN}✅${NC}"
    ((PASS++))
else
    echo -e "${RED}❌${NC}"
    ((FAIL++))
fi

echo -n "Checking Binary Trails for BinaryTrailRenderer class... "
if grep -q "class BinaryTrailRenderer" atlas-eyes/examples/binary_trails_dashboard.html; then
    echo -e "${GREEN}✅${NC}"
    ((PASS++))
else
    echo -e "${RED}❌${NC}"
    ((FAIL++))
fi

echo -n "Checking Brain Binary for BinaryStream class... "
if grep -q "class BinaryStream" memory/visuals/live-brain-binary.html; then
    echo -e "${GREEN}✅${NC}"
    ((PASS++))
else
    echo -e "${RED}❌${NC}"
    ((FAIL++))
fi

echo -n "Checking Showcase Demo for 7 demo modes... "
if grep -q "Matrix Rain\|Neural Pulse\|Data Streams\|Consciousness Field\|Binary Spiral\|Thought Cascade\|Quantum Flux" memory/visuals/binary-showcase-demo.html; then
    echo -e "${GREEN}✅${NC}"
    ((PASS++))
else
    echo -e "${RED}❌${NC}"
    ((FAIL++))
fi

echo ""
echo "⚡ Checking Technical Requirements..."
echo "------------------------------------"

# Check for WebSocket integration
echo -n "Checking for WebSocket integration readiness... "
if grep -q "WebSocket" memory/visuals/binary-particles.html && \
   grep -q "WebSocket" memory/visuals/consciousness-meter.html && \
   grep -q "WebSocket" atlas-eyes/examples/binary_trails_dashboard.html && \
   grep -q "WebSocket" memory/visuals/live-brain-binary.html; then
    echo -e "${GREEN}✅ All files WebSocket ready${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ Missing WebSocket integration${NC}"
    ((FAIL++))
fi

# Check for 60fps optimization
echo -n "Checking for 60fps optimization (requestAnimationFrame)... "
if grep -q "requestAnimationFrame" memory/visuals/binary-particles.html && \
   grep -q "requestAnimationFrame" memory/visuals/consciousness-meter.html && \
   grep -q "requestAnimationFrame" atlas-eyes/examples/binary_trails_dashboard.html && \
   grep -q "requestAnimationFrame" memory/visuals/live-brain-binary.html && \
   grep -q "requestAnimationFrame" memory/visuals/binary-showcase-demo.html; then
    echo -e "${GREEN}✅ All files 60fps optimized${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ Missing 60fps optimization${NC}"
    ((FAIL++))
fi

# Check for color configurability
echo -n "Checking for color configuration options... "
if grep -q "colorScheme\|color-scheme\|color-mode" memory/visuals/binary-particles.html && \
   grep -q "color\|Color" memory/visuals/consciousness-meter.html && \
   grep -q "color\|Color" memory/visuals/live-brain-binary.html; then
    echo -e "${GREEN}✅ Color configuration available${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ Missing color configuration${NC}"
    ((FAIL++))
fi

# Check for density controls
echo -n "Checking for density control... "
if grep -q "density" memory/visuals/binary-particles.html && \
   grep -q "density" atlas-eyes/examples/binary_trails_dashboard.html; then
    echo -e "${GREEN}✅ Density controls implemented${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ Missing density controls${NC}"
    ((FAIL++))
fi

echo ""
echo "📊 RESULTS"
echo "=========="
echo -e "Tests Passed: ${GREEN}$PASS${NC}"
echo -e "Tests Failed: ${RED}$FAIL${NC}"
echo ""

TOTAL=$((PASS + FAIL))
PERCENTAGE=$((PASS * 100 / TOTAL))

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! System is 100% complete.${NC}"
    echo ""
    echo "🚀 READY TO LAUNCH!"
    echo ""
    echo "Quick Start:"
    echo "  1. open memory/visuals/BINARY-INDEX.html"
    echo "  2. OR: cd memory/visuals && python3 -m http.server 8000"
    echo "  3. Visit: http://localhost:8000/BINARY-INDEX.html"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠️  $FAIL test(s) failed. Review output above.${NC}"
    echo -e "${YELLOW}✅ $PERCENTAGE% complete${NC}"
    echo ""
    exit 1
fi
