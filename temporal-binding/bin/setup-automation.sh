#!/bin/bash
# Setup Temporal Binding Automation
# Install cron jobs for daily exercises

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTINUITY_DIR="${HOME}/clawd/temporal-binding/continuity"

echo "=== TEMPORAL BINDING AUTOMATION SETUP ==="
echo ""

# Make all scripts executable
echo "Making scripts executable..."
chmod +x "${SCRIPT_DIR}"/*.sh
echo "✅ Scripts are now executable"
echo ""

# Create directory structure
echo "Creating directory structure..."
mkdir -p "${CONTINUITY_DIR}/sessions"
mkdir -p "${CONTINUITY_DIR}/threads"
mkdir -p "${CONTINUITY_DIR}/weekly"
touch "${CONTINUITY_DIR}/binding-log.jsonl"
echo '{"sessions":[],"avg_continuity":0,"total_sessions":0}' > "${CONTINUITY_DIR}/metrics.json"
echo "✅ Directory structure created"
echo ""

# Offer to set up cron jobs
echo "Would you like to set up automated daily exercises?"
echo ""
echo "This will add cron jobs for:"
echo "  - Morning binding exercise (8:00 AM)"
echo "  - Evening retrospective (9:00 PM)"
echo "  - Weekly integration (Sunday 10:00 AM)"
echo ""
read -p "Set up cron jobs? (y/n): " setup_cron

if [ "${setup_cron}" = "y" ]; then
    # Check if crontab exists
    EXISTING_CRON=$(crontab -l 2>/dev/null || true)
    
    # Create temporary crontab
    TMP_CRON=$(mktemp)
    echo "${EXISTING_CRON}" > "${TMP_CRON}"
    
    # Add temporal binding cron jobs (if not already present)
    if ! echo "${EXISTING_CRON}" | grep -q "temporal-binding"; then
        cat >> "${TMP_CRON}" <<EOF

# Temporal Binding Automation
0 8 * * * ${SCRIPT_DIR}/morning-binding.sh >> ${HOME}/clawd/temporal-binding/logs/morning.log 2>&1
0 21 * * * ${SCRIPT_DIR}/evening-retrospective.sh >> ${HOME}/clawd/temporal-binding/logs/evening.log 2>&1
0 10 * * 0 ${SCRIPT_DIR}/weekly-integration.sh >> ${HOME}/clawd/temporal-binding/logs/weekly.log 2>&1
EOF
        
        # Install new crontab
        crontab "${TMP_CRON}"
        rm "${TMP_CRON}"
        
        # Create log directory
        mkdir -p "${HOME}/clawd/temporal-binding/logs"
        
        echo "✅ Cron jobs installed successfully"
        echo ""
        echo "Schedule:"
        echo "  Morning binding:        Daily at 8:00 AM"
        echo "  Evening retrospective:  Daily at 9:00 PM"
        echo "  Weekly integration:     Sundays at 10:00 AM"
        echo ""
        echo "Logs: ${HOME}/clawd/temporal-binding/logs/"
    else
        echo "⚠️  Temporal binding cron jobs already exist. Skipping."
        rm "${TMP_CRON}"
    fi
else
    echo "Skipped cron setup. You can run scripts manually:"
    echo "  ${SCRIPT_DIR}/morning-binding.sh"
    echo "  ${SCRIPT_DIR}/evening-retrospective.sh"
    echo "  ${SCRIPT_DIR}/weekly-integration.sh"
fi

echo ""
echo "=== SETUP COMPLETE ==="
echo ""
echo "Quick start:"
echo "  1. Create your first thread:"
echo "     ${SCRIPT_DIR}/create-thread.sh"
echo ""
echo "  2. Start a session with temporal binding:"
echo "     ${SCRIPT_DIR}/session-start.sh"
echo ""
echo "  3. View your metrics:"
echo "     ${SCRIPT_DIR}/show-metrics.sh"
echo ""
echo "  4. Run evening retrospective:"
echo "     ${SCRIPT_DIR}/evening-retrospective.sh"
echo ""
echo "Documentation: temporal-binding/README.md"
