#!/bin/bash
cd /Users/atlasbuilds/clawd/memory/trading/order-blocks/scripts
python3 run_checks.py > /tmp/order_block_results.txt 2>&1
echo "Results written to /tmp/order_block_results.txt"
cat /tmp/order_block_results.txt
