#!/bin/bash
# Production Build Script for S2RTool Frontend
# Optimizes JavaScript files for production deployment

set -e  # Exit on error

echo "🚀 Building S2RTool Frontend for Production"
echo "=" * 60

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create build directory
BUILD_DIR="build"
echo -e "${YELLOW}📁 Creating build directory...${NC}"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Copy HTML files
echo -e "${YELLOW}📋 Copying HTML files...${NC}"
cp *.html "$BUILD_DIR/"

# Copy CSS files
echo -e "${YELLOW}🎨 Copying CSS files...${NC}"
cp style.css "$BUILD_DIR/"

# JavaScript files to minify
JS_FILES=(
    "utils.js"
    "script.js"
    "building-script.js"
    "planning-script.js"
    "planning-detail-script.js"
    "settings.js"
)

echo -e "${YELLOW}⚡ Minifying JavaScript files...${NC}"

# Simple minification using Python (no external deps needed)
for js_file in "${JS_FILES[@]}"; do
    if [ -f "$js_file" ]; then
        echo "  Processing $js_file..."

        # Simple minification:
        # 1. Remove comments (// and /* */)
        # 2. Remove excessive whitespace
        # 3. Keep one space where needed for syntax
        python3 << EOF > "$BUILD_DIR/$js_file"
import re

with open("$js_file", "r", encoding="utf-8") as f:
    content = f.read()

# Remove single-line comments (but keep URLs)
content = re.sub(r'(?<!:)//.*?$', '', content, flags=re.MULTILINE)

# Remove multi-line comments
content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

# Remove excessive whitespace while preserving necessary spaces
content = re.sub(r'\n\s*\n', '\n', content)  # Multiple newlines -> single
content = re.sub(r'[ \t]+', ' ', content)     # Multiple spaces -> single
content = re.sub(r'\s*([{};,:])\s*', r'\1', content)  # Remove space around punctuation
content = re.sub(r'\s*=\s*', '=', content)    # Remove space around =

# Trim each line
lines = [line.strip() for line in content.split('\n') if line.strip()]
print('\n'.join(lines))
EOF

        original_size=$(stat -f%z "$js_file" 2>/dev/null || stat -c%s "$js_file")
        minified_size=$(stat -f%z "$BUILD_DIR/$js_file" 2>/dev/null || stat -c%s "$BUILD_DIR/$js_file")
        reduction=$(( (original_size - minified_size) * 100 / original_size ))

        echo -e "${GREEN}    ✓ $js_file: $original_size → $minified_size bytes (-$reduction%)${NC}"
    else
        echo "    ⚠️  $js_file not found, skipping"
    fi
done

# Calculate total savings
echo ""
echo -e "${YELLOW}📊 Build Statistics:${NC}"

total_original=0
total_minified=0

for js_file in "${JS_FILES[@]}"; do
    if [ -f "$js_file" ]; then
        original_size=$(stat -f%z "$js_file" 2>/dev/null || stat -c%s "$js_file")
        minified_size=$(stat -f%z "$BUILD_DIR/$js_file" 2>/dev/null || stat -c%s "$BUILD_DIR/$BUILD_DIR/$js_file")
        total_original=$((total_original + original_size))
        total_minified=$((total_minified + minified_size))
    fi
done

total_reduction=$(( (total_original - total_minified) * 100 / total_original ))

echo "  Original size: $(echo "scale=2; $total_original / 1024" | bc) KB"
echo "  Minified size: $(echo "scale=2; $total_minified / 1024" | bc) KB"
echo -e "${GREEN}  Total reduction: $total_reduction%${NC}"

echo ""
echo -e "${GREEN}✅ Production build complete!${NC}"
echo ""
echo "📦 Build output: $BUILD_DIR/"
echo ""
echo "Next steps:"
echo "1. Review build output: ls -lh $BUILD_DIR/"
echo "2. Test production build"
echo "3. Deploy $BUILD_DIR/ to production server"
echo ""
echo "To use production build with Docker:"
echo "  Update frontend/Dockerfile to COPY from $BUILD_DIR/"
echo "=" * 60
