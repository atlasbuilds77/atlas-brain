#!/bin/bash
# detect-mode-switch.sh - Detects intent to switch routing modes

MESSAGE_TEXT="$1"

# Convert to lowercase for matching
MESSAGE_LOWER=$(echo "$MESSAGE_TEXT" | tr '[:upper:]' '[:lower:]')

# Switch to direct mode signals
DIRECT_SIGNALS=(
    "move to private"
    "switch to dm"
    "go private"
    "talk privately"
    "direct message me"
    "privately"
    "just you and me"
    "one on one"
    "between us"
)

# Switch to group mode signals
GROUP_SIGNALS=(
    "back to group"
    "rejoin group"
    "return to group"
    "group chat"
    "everyone"
    "tell everyone"
    "back to the group"
)

# Check for DM marker (case-insensitive)
if echo "$MESSAGE_TEXT" | grep -q "DM"; then
    echo "mode:direct"
    exit 0
fi

# Check for direct mode signals
for signal in "${DIRECT_SIGNALS[@]}"; do
    if echo "$MESSAGE_LOWER" | grep -qF "$signal"; then
        echo "mode:direct"
        exit 0
    fi
done

# Check for group mode signals
for signal in "${GROUP_SIGNALS[@]}"; do
    if echo "$MESSAGE_LOWER" | grep -qF "$signal"; then
        echo "mode:group"
        exit 0
    fi
done

# No mode switch detected
echo "mode:none"
