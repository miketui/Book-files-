#!/bin/bash

# Spelling validation script for Book-files project
# Validates spelling in XHTML files using multiple spell checkers

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_FILE="$SCRIPT_DIR/spelling-report.txt"
ERROR_COUNT=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "===========================================" > "$REPORT_FILE"
echo "SPELLING VALIDATION REPORT" >> "$REPORT_FILE"
echo "Generated: $(date)" >> "$REPORT_FILE"
echo "===========================================" >> "$REPORT_FILE"

echo -e "${GREEN}Starting spelling validation...${NC}"
echo "Report will be saved to: $REPORT_FILE"

# Function to extract text from XHTML files
extract_text_from_xhtml() {
    local file="$1"
    # Use xmlstarlet to extract text content, removing HTML tags
    xmlstarlet sel -t -v "//text()[not(ancestor::script)]" "$file" 2>/dev/null | \
    sed 's/&amp;/\&/g; s/&lt;/</g; s/&gt;/>/g; s/&quot;/"/g; s/&apos;/'\''/g' | \
    tr -s ' \n\t' ' ' | \
    sed 's/[[:space:]]*$//' | \
    sed 's/^[[:space:]]*//'
}

# Function to check spelling with aspell
check_with_aspell() {
    local file="$1"
    local text_file="/tmp/$(basename "$file").txt"
    
    extract_text_from_xhtml "$file" > "$text_file"
    
    if [[ -s "$text_file" ]]; then
        echo "  → Running aspell check..."
        # Use aspell to check spelling, ignoring common EPUB/HTML terms
        aspell list --personal="$SCRIPT_DIR/aspell-personal.txt" < "$text_file" | sort | uniq
    fi
    
    rm -f "$text_file"
}

# Function to check spelling with hunspell
check_with_hunspell() {
    local file="$1"
    local text_file="/tmp/$(basename "$file").txt"
    
    extract_text_from_xhtml "$file" > "$text_file"
    
    if [[ -s "$text_file" ]]; then
        echo "  → Running hunspell check..."
        # Use hunspell to check spelling
        hunspell -l -d en_US < "$text_file" | sort | uniq
    fi
    
    rm -f "$text_file"
}

# Create personal dictionary for EPUB/styling terms
create_personal_dictionary() {
    cat > "$SCRIPT_DIR/aspell-personal.txt" << 'EOF'
personal_ws-1.1 en 200
XHTML
EPUB
CSS
hairstyling
cosmetology
DevaCurl
SMART
mentorship
freelance
textured
hairstylists
entrepreneurship
blog
networking
mindfulness
wellness
stylesheet
WCAG
accessibility
ARIA
ISBN
OPF
mimetype
EOF
}

# Main validation function
validate_file() {
    local file="$1"
    
    if [[ ! -f "$file" ]]; then
        echo -e "${RED}File not found: $file${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Validating spelling in: $(basename "$file")${NC}"
    echo "" >> "$REPORT_FILE"
    echo "File: $file" >> "$REPORT_FILE"
    echo "----------------------------------------" >> "$REPORT_FILE"
    
    # Check if file is XHTML
    if [[ "$file" =~ \.xhtml$ ]]; then
        local aspell_errors
        local hunspell_errors
        
        aspell_errors=$(check_with_aspell "$file")
        hunspell_errors=$(check_with_hunspell "$file")
        
        if [[ -n "$aspell_errors" ]] || [[ -n "$hunspell_errors" ]]; then
            echo "SPELLING ERRORS FOUND:" >> "$REPORT_FILE"
            
            if [[ -n "$aspell_errors" ]]; then
                echo "Aspell detected errors:" >> "$REPORT_FILE"
                echo "$aspell_errors" >> "$REPORT_FILE"
                ERROR_COUNT=$((ERROR_COUNT + $(echo "$aspell_errors" | wc -l)))
            fi
            
            if [[ -n "$hunspell_errors" ]]; then
                echo "Hunspell detected errors:" >> "$REPORT_FILE"
                echo "$hunspell_errors" >> "$REPORT_FILE"
            fi
            
            echo -e "${RED}  ✗ Spelling errors found${NC}"
        else
            echo "No spelling errors detected." >> "$REPORT_FILE"
            echo -e "${GREEN}  ✓ No spelling errors${NC}"
        fi
    else
        echo "Skipped (not XHTML file)" >> "$REPORT_FILE"
        echo -e "${YELLOW}  - Skipped (not XHTML)${NC}"
    fi
}

# Create personal dictionary if it doesn't exist
if [[ ! -f "$SCRIPT_DIR/aspell-personal.txt" ]]; then
    create_personal_dictionary
fi

# Check if arguments provided
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <xhtml-file> [<xhtml-file> ...]"
    echo "       $0 *.xhtml  # validate all XHTML files"
    echo "       $0 --all    # validate all XHTML files in directory"
    exit 1
fi

# Handle --all option
if [[ "$1" == "--all" ]]; then
    set -- *.xhtml
fi

# Validate each file
for file in "$@"; do
    validate_file "$file"
done

# Summary
echo "" >> "$REPORT_FILE"
echo "===========================================" >> "$REPORT_FILE"
echo "SUMMARY" >> "$REPORT_FILE"
echo "Files processed: $#" >> "$REPORT_FILE"
echo "Total potential errors: $ERROR_COUNT" >> "$REPORT_FILE"
echo "===========================================" >> "$REPORT_FILE"

echo ""
echo -e "${GREEN}Spelling validation completed!${NC}"
echo "Files processed: $#"
echo "Total potential errors: $ERROR_COUNT"
echo "Report saved to: $REPORT_FILE"

if [[ $ERROR_COUNT -gt 0 ]]; then
    echo -e "${YELLOW}Please review the spelling report for potential issues.${NC}"
    exit 1
else
    echo -e "${GREEN}No spelling errors detected in processed files.${NC}"
    exit 0
fi