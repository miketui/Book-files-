#!/bin/bash

# Master validation pipeline for Book-files project
# Runs comprehensive validation including XML, EPUB, spelling, grammar, and fact-checking

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_DIR="$SCRIPT_DIR/validation_reports_$TIMESTAMP"
SUMMARY_FILE="$REPORT_DIR/validation_summary.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Validation results
XML_RESULT=0
EPUB_RESULT=0
SPELLING_RESULT=0
GRAMMAR_RESULT=0
FACTS_RESULT=0

# Create report directory
mkdir -p "$REPORT_DIR"

# Function to print colored headers
print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE} $1 ${NC}"
    echo -e "${BLUE}============================================${NC}"
}

# Function to print status
print_status() {
    if [[ $1 -eq 0 ]]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
    fi
}

# Initialize summary file
init_summary() {
    cat > "$SUMMARY_FILE" << EOF
====================================================================
COMPREHENSIVE VALIDATION PIPELINE SUMMARY
====================================================================
Generated: $(date)
Project: Book-files EPUB validation
Report Directory: $REPORT_DIR
====================================================================

VALIDATION STAGES EXECUTED:
EOF
}

# Function to run XML/XHTML validation
run_xml_validation() {
    print_header "XML/XHTML VALIDATION"
    
    if [[ -f "$SCRIPT_DIR/validate-xml.sh" ]]; then
        echo "Running XML/XHTML validation on all .xhtml files..."
        
        # Run validation and capture output
        "$SCRIPT_DIR/validate-xml.sh" *.xhtml > "$REPORT_DIR/xml_validation.log" 2>&1
        XML_RESULT=$?
        
        print_status $XML_RESULT "XML/XHTML validation completed"
        
        if [[ $XML_RESULT -eq 0 ]]; then
            echo "All XHTML files passed XML validation"
        else
            echo "Some XHTML files have XML validation issues - see $REPORT_DIR/xml_validation.log"
        fi
    else
        echo -e "${YELLOW}Warning: validate-xml.sh not found, skipping XML validation${NC}"
        XML_RESULT=1
    fi
    
    echo ""
}

# Function to run EPUB validation
run_epub_validation() {
    print_header "EPUB VALIDATION"
    
    if [[ -f "$SCRIPT_DIR/validate-epub.sh" ]]; then
        echo "Running EPUB validation..."
        
        # Check if EPUB file exists
        if [[ -f "curls-and-contemplation.epub" ]]; then
            "$SCRIPT_DIR/validate-epub.sh" > "$REPORT_DIR/epub_validation.log" 2>&1
            EPUB_RESULT=$?
            
            print_status $EPUB_RESULT "EPUB validation completed"
            
            if [[ $EPUB_RESULT -eq 0 ]]; then
                echo "EPUB file passed validation"
            else
                echo "EPUB file has validation issues - see $REPORT_DIR/epub_validation.log"
            fi
        else
            echo -e "${YELLOW}Warning: curls-and-contemplation.epub not found, skipping EPUB validation${NC}"
            EPUB_RESULT=1
        fi
    else
        echo -e "${YELLOW}Warning: validate-epub.sh not found, skipping EPUB validation${NC}"
        EPUB_RESULT=1
    fi
    
    echo ""
}

# Function to run spelling validation
run_spelling_validation() {
    print_header "SPELLING VALIDATION"
    
    if [[ -f "$SCRIPT_DIR/validate-spelling.sh" ]]; then
        echo "Running spelling validation on all .xhtml files..."
        
        "$SCRIPT_DIR/validate-spelling.sh" *.xhtml
        SPELLING_RESULT=$?
        
        # Move spelling report to report directory
        if [[ -f "spelling-report.txt" ]]; then
            mv "spelling-report.txt" "$REPORT_DIR/"
        fi
        
        print_status $SPELLING_RESULT "Spelling validation completed"
        
        if [[ $SPELLING_RESULT -eq 0 ]]; then
            echo "No spelling errors found"
        else
            echo "Potential spelling errors found - see $REPORT_DIR/spelling-report.txt"
        fi
    else
        echo -e "${YELLOW}Warning: validate-spelling.sh not found, skipping spelling validation${NC}"
        SPELLING_RESULT=1
    fi
    
    echo ""
}

# Function to run grammar validation
run_grammar_validation() {
    print_header "GRAMMAR VALIDATION"
    
    if [[ -f "$SCRIPT_DIR/validate-grammar.py" ]]; then
        echo "Running grammar and readability validation..."
        echo "This may take several minutes for LanguageTool initialization..."
        
        python3 "$SCRIPT_DIR/validate-grammar.py" --all --output "$REPORT_DIR/grammar-report.txt"
        GRAMMAR_RESULT=$?
        
        print_status $GRAMMAR_RESULT "Grammar validation completed"
        
        if [[ $GRAMMAR_RESULT -eq 0 ]]; then
            echo "Grammar validation completed - see $REPORT_DIR/grammar-report.txt for readability analysis"
        else
            echo "Grammar issues found - see $REPORT_DIR/grammar-report.txt"
        fi
    else
        echo -e "${YELLOW}Warning: validate-grammar.py not found, skipping grammar validation${NC}"
        GRAMMAR_RESULT=1
    fi
    
    echo ""
}

# Function to run fact-checking validation
run_fact_checking() {
    print_header "FACT-CHECKING VALIDATION"
    
    if [[ -f "$SCRIPT_DIR/validate-facts.py" ]]; then
        echo "Running fact-checking and bibliography validation..."
        
        python3 "$SCRIPT_DIR/validate-facts.py" --all --output "$REPORT_DIR/fact-check-report.txt"
        FACTS_RESULT=$?
        
        print_status $FACTS_RESULT "Fact-checking validation completed"
        
        if [[ $FACTS_RESULT -eq 0 ]]; then
            echo "Fact-checking completed - see $REPORT_DIR/fact-check-report.txt for analysis"
        else
            echo "Fact-checking issues found - see $REPORT_DIR/fact-check-report.txt"
        fi
    else
        echo -e "${YELLOW}Warning: validate-facts.py not found, skipping fact-checking validation${NC}"
        FACTS_RESULT=1
    fi
    
    echo ""
}

# Function to generate final summary
generate_summary() {
    print_header "VALIDATION SUMMARY"
    
    # Calculate overall result
    TOTAL_ERRORS=$((XML_RESULT + EPUB_RESULT + SPELLING_RESULT + GRAMMAR_RESULT + FACTS_RESULT))
    
    # Append to summary file
    cat >> "$SUMMARY_FILE" << EOF

1. XML/XHTML Validation: $([ $XML_RESULT -eq 0 ] && echo "PASSED" || echo "FAILED")
2. EPUB Validation: $([ $EPUB_RESULT -eq 0 ] && echo "PASSED" || echo "FAILED")
3. Spelling Validation: $([ $SPELLING_RESULT -eq 0 ] && echo "PASSED" || echo "FAILED")
4. Grammar Validation: $([ $GRAMMAR_RESULT -eq 0 ] && echo "PASSED" || echo "FAILED")
5. Fact-checking Validation: $([ $FACTS_RESULT -eq 0 ] && echo "PASSED" || echo "FAILED")

====================================================================
OVERALL RESULT: $([ $TOTAL_ERRORS -eq 0 ] && echo "ALL VALIDATIONS PASSED" || echo "$TOTAL_ERRORS VALIDATIONS FAILED")
====================================================================

REPORT FILES GENERATED:
- $REPORT_DIR/xml_validation.log
- $REPORT_DIR/epub_validation.log  
- $REPORT_DIR/spelling-report.txt
- $REPORT_DIR/grammar-report.txt
- $REPORT_DIR/fact-check-report.txt

NEXT STEPS:
1. Review all report files for specific issues
2. Address any validation failures
3. Manually verify factual claims identified in fact-check report
4. Re-run validation after fixes

====================================================================
EOF
    
    # Display summary on screen
    echo "Validation Results:"
    print_status $XML_RESULT "XML/XHTML Validation"
    print_status $EPUB_RESULT "EPUB Validation" 
    print_status $SPELLING_RESULT "Spelling Validation"
    print_status $GRAMMAR_RESULT "Grammar Validation"
    print_status $FACTS_RESULT "Fact-checking Validation"
    
    echo ""
    if [[ $TOTAL_ERRORS -eq 0 ]]; then
        echo -e "${GREEN}🎉 ALL VALIDATIONS PASSED! 🎉${NC}"
    else
        echo -e "${RED}❌ $TOTAL_ERRORS validations failed${NC}"
        echo -e "${YELLOW}Please review the reports in: $REPORT_DIR${NC}"
    fi
    
    echo ""
    echo "Summary report saved to: $SUMMARY_FILE"
    echo "All validation reports saved in: $REPORT_DIR"
}

# Main execution
main() {
    echo -e "${MAGENTA}Starting Comprehensive EPUB Validation Pipeline${NC}"
    echo -e "${MAGENTA}================================================${NC}"
    echo ""
    
    # Initialize summary
    init_summary
    
    # Run all validation stages
    run_xml_validation
    run_epub_validation
    run_spelling_validation
    run_grammar_validation
    run_fact_checking
    
    # Generate final summary
    generate_summary
    
    # Exit with appropriate code
    TOTAL_ERRORS=$((XML_RESULT + EPUB_RESULT + SPELLING_RESULT + GRAMMAR_RESULT + FACTS_RESULT))
    exit $TOTAL_ERRORS
}

# Help function
show_help() {
    cat << EOF
Comprehensive EPUB Validation Pipeline

USAGE:
    $0 [options]

OPTIONS:
    --help          Show this help message
    --xml-only      Run only XML/XHTML validation
    --epub-only     Run only EPUB validation  
    --spelling-only Run only spelling validation
    --grammar-only  Run only grammar validation
    --facts-only    Run only fact-checking validation

EXAMPLES:
    $0                  # Run all validations
    $0 --spelling-only  # Run only spelling check
    $0 --help          # Show this help

REPORTS:
    All validation reports are saved in validation_reports_TIMESTAMP/ directory
    A summary report is generated showing overall results

REQUIREMENTS:
    - xmlstarlet, tidy (for XML validation)
    - Java, epubcheck (for EPUB validation)
    - aspell, hunspell (for spelling validation)
    - Python 3 with language-tool-python, textstat, beautifulsoup4 (for grammar/facts)
EOF
}

# Parse command line arguments
case "${1:-}" in
    --help)
        show_help
        exit 0
        ;;
    --xml-only)
        init_summary
        run_xml_validation
        generate_summary
        exit $XML_RESULT
        ;;
    --epub-only)
        init_summary
        run_epub_validation
        generate_summary
        exit $EPUB_RESULT
        ;;
    --spelling-only)
        init_summary
        run_spelling_validation
        generate_summary
        exit $SPELLING_RESULT
        ;;
    --grammar-only)
        init_summary
        run_grammar_validation
        generate_summary
        exit $GRAMMAR_RESULT
        ;;
    --facts-only)
        init_summary
        run_fact_checking
        generate_summary
        exit $FACTS_RESULT
        ;;
    "")
        # Run all validations
        main
        ;;
    *)
        echo "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac