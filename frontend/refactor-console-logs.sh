#!/bin/bash
# Refactor Script: Replace console.log with production-safe log()
# This script updates JavaScript files to use utils.js logging functions

echo "🔧 Refactoring JavaScript files to use utils.js..."

# Files to refactor
FILES=(
    "building-script.js"
    "script.js"
    "planning-script.js"
    "planning-detail-script.js"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "📝 Processing $file..."

        # Backup original
        cp "$file" "$file.backup"

        # Replace console.log with log
        sed -i 's/console\.log(/log(/g' "$file"

        # Replace console.error with logError
        sed -i 's/console\.error(/logError(/g' "$file"

        # Replace console.warn with logWarn
        sed -i 's/console\.warn(/logWarn(/g' "$file"

        echo "✅ $file refactored"
    else
        echo "⚠️  $file not found"
    fi
done

echo ""
echo "🎉 Refactoring complete!"
echo ""
echo "Next steps:"
echo "1. Review changes: git diff frontend/*.js"
echo "2. Test all pages thoroughly"
echo "3. Remove .backup files if satisfied"
echo "4. Commit: git add . && git commit -m 'refactor: Use utils.js logging functions'"
