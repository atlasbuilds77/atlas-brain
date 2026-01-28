#!/bin/bash
# Test script for Atlas Eyes tremor detection and ROI API endpoints

echo "======================================================================"
echo "Atlas Eyes - Tremor Detection & ROI Tracking API Test"
echo "======================================================================"
echo ""

API_URL="http://127.0.0.1:5000"

# Check if server is running
echo "1. Checking server status..."
STATUS=$(curl -s ${API_URL}/api/status)
if [ $? -eq 0 ]; then
    echo "✅ Server is running"
    echo "   Response: ${STATUS}"
else
    echo "❌ Server not running. Start it with: cd src && python atlas_api.py"
    exit 1
fi
echo ""

# Start motion extraction if not already running
echo "2. Starting motion extraction..."
START_RESPONSE=$(curl -s -X POST ${API_URL}/api/start -H "Content-Type: application/json" -d '{"algorithm": "frame_diff"}')
echo "   Response: ${START_RESPONSE}"
echo ""

# Wait for data collection
echo "3. Waiting 5 seconds for data collection..."
sleep 5
echo ""

# Test basic motion endpoint
echo "4. Testing /api/motion endpoint..."
curl -s ${API_URL}/api/motion | jq '.'
echo ""

# Test tremor detection endpoint
echo "5. Testing /api/tremor endpoint..."
TREMOR_DATA=$(curl -s ${API_URL}/api/tremor)
echo "${TREMOR_DATA}" | jq '.'
echo ""

TREMOR_DETECTED=$(echo "${TREMOR_DATA}" | jq -r '.detected')
if [ "${TREMOR_DETECTED}" == "true" ]; then
    FREQ=$(echo "${TREMOR_DATA}" | jq -r '.frequency_hz')
    CONF=$(echo "${TREMOR_DATA}" | jq -r '.confidence')
    echo "⚠️  TREMOR DETECTED: ${FREQ} Hz (confidence: ${CONF})"
else
    echo "✅ No tremor detected"
fi
echo ""

# Test heartbeat detection endpoint
echo "6. Testing /api/heartbeat endpoint..."
HEARTBEAT_DATA=$(curl -s ${API_URL}/api/heartbeat)
echo "${HEARTBEAT_DATA}" | jq '.'
echo ""

HB_DETECTED=$(echo "${HEARTBEAT_DATA}" | jq -r '.detected')
if [ "${HB_DETECTED}" == "true" ]; then
    BPM=$(echo "${HEARTBEAT_DATA}" | jq -r '.bpm')
    echo "♥  HEARTBEAT DETECTED: ${BPM} BPM"
else
    echo "⏳ No heartbeat detected (may need more time)"
fi
echo ""

# Test NEW ROI endpoint
echo "7. Testing /api/roi endpoint (NEW!)..."
ROI_DATA=$(curl -s ${API_URL}/api/roi)
echo "${ROI_DATA}" | jq '.'
echo ""

# Parse ROI data
HANDS_COUNT=$(echo "${ROI_DATA}" | jq -r '.rois.hands | length')
HAS_FACE=$(echo "${ROI_DATA}" | jq -r '.rois.face != null')
HAS_CHEST=$(echo "${ROI_DATA}" | jq -r '.rois.chest != null')

echo "   ROI Detection Summary:"
echo "   - Hands detected: ${HANDS_COUNT}"
echo "   - Face detected: ${HAS_FACE}"
echo "   - Chest detected: ${HAS_CHEST}"
echo ""

# Check per-ROI tremor detection
echo "8. Per-ROI Tremor Analysis:"

for ROI in left_hand right_hand face chest; do
    TREMOR_DETECTED=$(echo "${ROI_DATA}" | jq -r ".motion_analysis.${ROI}.tremor.detected // false")
    TREMOR_READY=$(echo "${ROI_DATA}" | jq -r ".motion_analysis.${ROI}.tremor.ready // false")
    
    if [ "${TREMOR_DETECTED}" == "true" ]; then
        FREQ=$(echo "${ROI_DATA}" | jq -r ".motion_analysis.${ROI}.tremor.frequency_hz")
        CONF=$(echo "${ROI_DATA}" | jq -r ".motion_analysis.${ROI}.tremor.confidence")
        echo "   ⚠️  ${ROI}: TREMOR at ${FREQ} Hz (confidence: ${CONF})"
    elif [ "${TREMOR_READY}" == "true" ]; then
        echo "   ✅ ${ROI}: No tremor detected"
    else
        FILL=$(echo "${ROI_DATA}" | jq -r ".motion_analysis.${ROI}.tremor.buffer_fill // 0")
        FILL_PCT=$(echo "scale=0; ${FILL} * 100 / 1" | bc)
        echo "   ⏳ ${ROI}: Collecting data (${FILL_PCT}%)"
    fi
done
echo ""

# Test frequency spectrum endpoint
echo "9. Testing /api/frequency endpoint..."
FREQ_DATA=$(curl -s ${API_URL}/api/frequency | jq '{ready: .ready, sample_count: .sample_count, num_frequencies: (.frequencies | length)}')
echo "${FREQ_DATA}"
echo ""

echo "======================================================================"
echo "✅ API Test Complete!"
echo "======================================================================"
echo ""
echo "Summary of endpoints tested:"
echo "  ✅ GET  /api/status"
echo "  ✅ POST /api/start"
echo "  ✅ GET  /api/motion"
echo "  ✅ GET  /api/tremor"
echo "  ✅ GET  /api/heartbeat"
echo "  ✅ GET  /api/roi (NEW!)"
echo "  ✅ GET  /api/frequency"
echo ""
echo "To stop the server: curl -X POST ${API_URL}/api/stop"
echo ""
