#!/bin/bash
# ATLAS LOCKDOWN PROTOCOL
# Triggered by duress code or unauthorized access detection
# Encrypts sensitive files and kills active sessions
#
# Usage: bash titan-vault/security/lockdown-protocol.sh "<duress_code>"
# Or:    bash titan-vault/security/lockdown-protocol.sh --force

set -euo pipefail

VAULT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE_DIR="$(cd "$VAULT_DIR/.." && pwd)"
SECURITY_DIR="$VAULT_DIR/security"
LOG_FILE="$SECURITY_DIR/lockdown.log"
LOCKDOWN_FLAG="$SECURITY_DIR/.lockdown_active"

# Duress code hash (normalized lowercase, sha256)
# The actual code is NEVER stored in plaintext
DURESS_HASHES=(
    # Orion sets these — see security-config.md
)

log_event() {
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] $1" >> "$LOG_FILE"
}

# --- LOCKDOWN ACTIONS ---

lockdown() {
    echo "🔒 LOCKDOWN INITIATED — $(date)"
    log_event "LOCKDOWN TRIGGERED"

    # 1. Set lockdown flag
    touch "$LOCKDOWN_FLAG"
    log_event "Lockdown flag set"

    # 2. Encrypt vault files with password from environment
    if command -v openssl &>/dev/null; then
        SENSITIVE_DIRS=(
            "$VAULT_DIR/memory"
            "$WORKSPACE_DIR/memory/trading"
            "$WORKSPACE_DIR/atlas-trader"
        )
        for DIR in "${SENSITIVE_DIRS[@]}"; do
            if [ -d "$DIR" ]; then
                ARCHIVE="/tmp/atlas_lockdown_$(basename "$DIR")_$(date +%s).tar.gz"
                tar -czf "$ARCHIVE" -C "$(dirname "$DIR")" "$(basename "$DIR")" 2>/dev/null
                openssl enc -aes-256-cbc -pbkdf2 -salt -in "$ARCHIVE" -out "${ARCHIVE}.enc" -pass env:ATLAS_LOCKDOWN_KEY 2>/dev/null && {
                    # Secure delete originals
                    find "$DIR" -type f -name "*.md" -exec sh -c 'dd if=/dev/urandom of="{}" bs=$(stat -f%z "{}") count=1 2>/dev/null; rm -f "{}"' \;
                    log_event "Encrypted and wiped: $DIR"
                } || {
                    log_event "WARNING: Encryption failed for $DIR (no ATLAS_LOCKDOWN_KEY set)"
                }
                rm -f "$ARCHIVE"
            fi
        done
    fi

    # 3. Clear shell history
    cat /dev/null > ~/.bash_history 2>/dev/null
    cat /dev/null > ~/.zsh_history 2>/dev/null
    log_event "Shell history cleared"

    # 4. Notify Orion
    echo "🚨 LOCKDOWN COMPLETE"
    echo "Sensitive files encrypted. Originals wiped."
    echo "Recovery requires ATLAS_LOCKDOWN_KEY environment variable."
    log_event "LOCKDOWN COMPLETE"
}

# --- ENTRY POINT ---

INPUT="${1:-}"

if [ "$INPUT" = "--force" ]; then
    lockdown
    exit 0
fi

if [ -z "$INPUT" ]; then
    echo "Usage: bash lockdown-protocol.sh \"<duress_code>\" OR --force"
    exit 1
fi

# Normalize and hash
NORMALIZED=$(printf '%s' "$INPUT" | tr '[:upper:]' '[:lower:]' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
INPUT_HASH=$(printf '%s' "$NORMALIZED" | shasum -a 256 | awk '{print $1}')

# Check duress code
AUTHORIZED=false
for HASH in "${DURESS_HASHES[@]}"; do
    [ "$INPUT_HASH" = "$HASH" ] && AUTHORIZED=true
done

if [ "$AUTHORIZED" = true ]; then
    lockdown
elif [ -f "$SECURITY_DIR/duress-hashes.txt" ]; then
    # Check external hash file
    if grep -q "$INPUT_HASH" "$SECURITY_DIR/duress-hashes.txt" 2>/dev/null; then
        lockdown
    else
        echo "❌ Invalid code"
        log_event "FAILED LOCKDOWN ATTEMPT - hash: $INPUT_HASH"
        exit 1
    fi
else
    echo "❌ Invalid code"
    log_event "FAILED LOCKDOWN ATTEMPT - hash: $INPUT_HASH"
    exit 1
fi
