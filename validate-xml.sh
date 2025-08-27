#!/bin/bash

# XML validation script for Book-files project
# Validates XHTML files for EPUB compliance

if [ $# -eq 0 ]; then
    echo "Usage: $0 <xhtml-file>"
    echo "       $0 *.xhtml  # validate all XHTML files"
    exit 1
fi

echo "XML/XHTML Validation Tools Available:"
echo "- xmlstarlet: $(xmlstarlet --version | head -1)"
echo "- tidy: $(tidy --version | head -1)"
echo ""

for file in "$@"; do
    if [ -f "$file" ]; then
        echo "Validating: $file"
        
        # Check well-formedness
        echo "  → Checking well-formedness..."
        xmlstarlet val -w "$file"
        
        # Check with HTML Tidy for XHTML compliance
        echo "  → Checking XHTML compliance..."
        tidy -xml -errors -quiet "$file" 2>&1 | head -10
        
        echo ""
    else
        echo "File not found: $file"
    fi
done