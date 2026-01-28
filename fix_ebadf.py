#!/usr/bin/env python3
import os
import subprocess
import time
import signal

# Kill any clawdbot processes
print("Killing clawdbot processes...")
os.system("pkill -f 'clawdbot.*gateway' 2>/dev/null || true")
time.sleep(2)

# Check if any are still running
result = subprocess.run(["pgrep", "-f", "clawdbot.*gateway"], capture_output=True)
if result.returncode == 0:
    print("Force killing remaining processes...")
    os.system("pkill -9 -f 'clawdbot.*gateway' 2>/dev/null || true")
    time.sleep(1)

# Now let's examine the problematic file
file_path = "/opt/homebrew/lib/node_modules/clawdbot/dist/agents/bash-tools.exec.js"
print(f"\nExamining {file_path}...")

# Read the file
with open(file_path, 'r') as f:
    content = f.read()

# Find all occurrences of detached:
lines = content.split('\n')
detached_lines = []
for i, line in enumerate(lines):
    if 'detached:' in line:
        detached_lines.append((i, line.strip()))

print(f"\nFound {len(detached_lines)} occurrences of 'detached:':")
for i, (line_num, line) in enumerate(detached_lines):
    print(f"{i+1}. Line {line_num+1}: {line}")

# Show context around each occurrence
print("\n\nContext around each occurrence:")
for i, (line_num, line) in enumerate(detached_lines):
    print(f"\n--- Occurrence {i+1} (Line {line_num+1}) ---")
    start = max(0, line_num - 2)
    end = min(len(lines), line_num + 3)
    for j in range(start, end):
        prefix = ">>> " if j == line_num else "    "
        print(f"{prefix}{j+1}: {lines[j]}")