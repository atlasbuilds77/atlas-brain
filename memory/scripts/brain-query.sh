#!/bin/bash
# Quick helper to read brain daemon index from anywhere
# Usage: bash memory/scripts/brain-query.sh [category|file|stats]

INDEX_FILE="/tmp/atlas-memory-index.json"

if [ ! -f "$INDEX_FILE" ]; then
    echo "❌ Brain daemon index not found at $INDEX_FILE"
    echo "   Start daemon: bash memory/scripts/brain-daemon-control.sh start"
    exit 1
fi

case "$1" in
    category)
        if [ -z "$2" ]; then
            echo "Usage: $0 category [protocols|trading|projects|people|tools|other]"
            exit 1
        fi
        node -e "
            const fs = require('fs');
            const index = JSON.parse(fs.readFileSync('$INDEX_FILE', 'utf8'));
            const category = '$2';
            if (!index.categories[category]) {
                console.log('Unknown category: $2');
                console.log('Available:', Object.keys(index.categories).join(', '));
                process.exit(1);
            }
            const files = index.categories[category];
            console.log('Category: ' + category + ' (' + files.length + ' files)\\n');
            files.forEach(f => {
                console.log('  ' + f.path);
                console.log('    ' + f.preview);
                console.log('');
            });
        "
        ;;
    
    file)
        if [ -z "$2" ]; then
            echo "Usage: $0 file [filename]"
            exit 1
        fi
        node -e "
            const fs = require('fs');
            const index = JSON.parse(fs.readFileSync('$INDEX_FILE', 'utf8'));
            const search = '$2';
            const matches = index.allFiles.filter(f => 
                f.name.includes(search) || f.path.includes(search)
            );
            if (matches.length === 0) {
                console.log('No files matching: $2');
            } else {
                console.log('Found ' + matches.length + ' matching files:\\n');
                matches.forEach(f => {
                    console.log('  ' + f.path);
                    console.log('    Size: ' + f.size + ' bytes');
                    console.log('    Modified: ' + f.modified);
                    console.log('    Preview: ' + f.preview);
                    console.log('');
                });
            }
        "
        ;;
    
    stats|"")
        node -e "
            const fs = require('fs');
            const index = JSON.parse(fs.readFileSync('$INDEX_FILE', 'utf8'));
            console.log('Brain Daemon Index Stats');
            console.log('========================\\n');
            console.log('Generated: ' + index.generated);
            console.log('Scan Count: ' + index.scanCount);
            console.log('Total Files: ' + index.totalFiles);
            console.log('\\nCategories:');
            for (const [key, value] of Object.entries(index.stats)) {
                console.log('  ' + key.padEnd(12) + ': ' + value + ' files');
            }
            console.log('\\nRecent Files (by modification):');
            const recent = index.allFiles
                .sort((a, b) => new Date(b.modified) - new Date(a.modified))
                .slice(0, 5);
            recent.forEach(f => {
                const date = new Date(f.modified);
                const ago = Math.round((Date.now() - date) / 1000 / 60);
                console.log('  ' + f.path + ' (' + ago + 'm ago)');
            });
        "
        ;;
    
    *)
        echo "Brain Daemon Query Tool"
        echo "======================="
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  stats               - Show index statistics (default)"
        echo "  category [name]     - List all files in category"
        echo "  file [search]       - Search for files by name/path"
        echo ""
        echo "Examples:"
        echo "  $0 stats"
        echo "  $0 category trading"
        echo "  $0 file active-positions"
        exit 1
        ;;
esac
