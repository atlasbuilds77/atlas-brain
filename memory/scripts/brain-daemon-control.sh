#!/bin/bash
case "$1" in
  start) nohup node memory/scripts/brain-daemon.js > /tmp/brain-daemon.log 2>&1 & echo $! > /tmp/brain-daemon.pid ;;
  stop) kill $(cat /tmp/brain-daemon.pid) ;;
  status) ps -p $(cat /tmp/brain-daemon.pid) ;;
esac
