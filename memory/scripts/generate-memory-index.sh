#!/bin/bash
# Generate memory index for brain auto-growth system
# Run this periodically or add to watch script

MEMORY_DIR="memory"
OUTPUT_FILE="/tmp/atlas-memory-index.json"

echo "{" > "$OUTPUT_FILE"
echo '  "files": [' >> "$OUTPUT_FILE"

# Find all .md files in memory/
first=true
find "$MEMORY_DIR" -name "*.md" -type f | while read -r file; do
    filename=$(basename "$file" .md)
    
    if [ "$first" = true ]; then
        first=false
    else
        echo "," >> "$OUTPUT_FILE"
    fi
    
    # Read first 500 characters for keyword extraction
    content=$(head -c 500 "$file" | tr '\n' ' ' | sed 's/"/\\"/g')
    
    echo -n "    {" >> "$OUTPUT_FILE"
    echo -n "\"path\": \"$file\", " >> "$OUTPUT_FILE"
    echo -n "\"name\": \"$filename\", " >> "$OUTPUT_FILE"
    echo -n "\"modified\": $(stat -f %m "$file" 2>/dev/null || stat -c %Y "$file"), " >> "$OUTPUT_FILE"
    echo -n "\"content\": \"$content\"" >> "$OUTPUT_FILE"
    echo -n "}" >> "$OUTPUT_FILE"
done

echo "" >> "$OUTPUT_FILE"
echo "  ]," >> "$OUTPUT_FILE"
echo "  \"timestamp\": $(date +%s)000," >> "$OUTPUT_FILE"
echo "  \"count\": $(find "$MEMORY_DIR" -name "*.md" -type f | wc -l)" >> "$OUTPUT_FILE"
echo "}" >> "$OUTPUT_FILE"

echo "✅ Memory index generated: $OUTPUT_FILE"
echo "   Total files: $(find "$MEMORY_DIR" -name "*.md" -type f | wc -l)"
