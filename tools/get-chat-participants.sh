#!/bin/bash
# Get participants for a given chat_id from iMessage database

set -euo pipefail

chat_id="${1:-}"

if [[ -z "$chat_id" ]]; then
  echo "Usage: $0 <chat_id>" >&2
  exit 1
fi

DB_PATH="$HOME/Library/Messages/chat.db"

if [[ ! -f "$DB_PATH" ]]; then
  echo "Error: iMessage database not found at $DB_PATH" >&2
  exit 1
fi

# Query for chat participants (use comma separator for GROUP_CONCAT)
sqlite3 "$DB_PATH" <<SQL
SELECT 
  chat.ROWID || '|' ||
  COALESCE(chat.chat_identifier, '') || '|' ||
  COALESCE(chat.display_name, '') || '|' ||
  COALESCE(GROUP_CONCAT(handle.id, ','), '') || '|' ||
  COUNT(handle.id)
FROM chat 
LEFT JOIN chat_handle_join ON chat.ROWID = chat_handle_join.chat_id 
LEFT JOIN handle ON chat_handle_join.handle_id = handle.ROWID 
WHERE chat.ROWID = $chat_id 
GROUP BY chat.ROWID;
SQL
