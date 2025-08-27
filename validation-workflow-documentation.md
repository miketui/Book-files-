# EPUB Validation Workflow Documentation

## Overview

This document describes the comprehensive validation workflow implemented for the "Curls & Contemplation" EPUB project. The validation system ensures content quality, technical compliance, and professional publishing standards.

## Validation Components

### 1. Core Validation Tools

#### XML/XHTML Validation (`validate-xml.sh`)
- **Purpose**: Validates XML well-formedness and XHTML compliance
- **Tools**: xmlstarlet, tidy-html5
- **Scope**: All `.xhtml` files
- **Output**: Console output with validation status

#### EPUB Structure Validation (`validate-epub.sh`)
- **Purpose**: Validates complete EPUB package against EPUB 3.2 standards
- **Tools**: EPUBCheck 4.2.6 with Java
- **Scope**: Complete EPUB file (`curls-and-contemplation.epub`)
- **Output**: Detailed validation report with errors/warnings

### 2. Content Quality Tools

#### Spelling Validation (`validate-spelling.sh`)
- **Purpose**: Checks spelling in extracted text content
- **Tools**: aspell, hunspell with custom dictionaries
- **Features**:
  - Custom personal dictionary for specialized terms
  - HTML entity decoding
  - Text extraction from XHTML
  - Duplicate error filtering
- **Output**: Detailed spelling report with potential errors

#### Grammar & Readability Validation (`validate-grammar.py`)
- **Purpose**: Analyzes grammar, style, and readability metrics
- **Tools**: LanguageTool (network-dependent), textstat, BeautifulSoup
- **Features**:
  - Grammar checking with suggestions
  - Readability analysis (Flesch Reading Ease, etc.)
  - Grade level assessment
  - Reading time estimation
- **Output**: Comprehensive grammar and readability report

#### Fact-Checking Validation (`validate-facts.py`)
- **Purpose**: Identifies factual claims and validates bibliography
- **Tools**: BeautifulSoup, requests for URL checking
- **Features**:
  - Bibliography entry extraction
  - URL accessibility testing
  - Factual claim identification
  - Citation pattern recognition
- **Output**: Fact-checking report with URL status and identified claims

### 3. Master Validation Pipeline (`validate-all.sh`)

The master script orchestrates all validation processes:

```bash
./validate-all.sh [options]
```

#### Available Options:
- `--xml-only`: Run only XML/XHTML validation
- `--epub-only`: Run only EPUB validation
- `--spelling-only`: Run only spelling validation
- `--grammar-only`: Run only grammar validation
- `--facts-only`: Run only fact-checking validation
- `--help`: Show usage information

#### Output Structure:
```
validation_reports_YYYYMMDD_HHMMSS/
├── validation_summary.txt          # Master summary
├── xml_validation.log              # XML validation results
├── epub_validation.log             # EPUB validation results
├── spelling-report.txt             # Spelling analysis
├── grammar-report.txt              # Grammar and readability
└── fact-check-report.txt          # Fact-checking results
```

## Usage Examples

### Quick Validation
```bash
# Run all validations
./validate-all.sh

# Check only spelling
./validate-all.sh --spelling-only

# Validate single file spelling
./validate-spelling.sh 1-TitlePage.xhtml
```

### Individual Tool Usage
```bash
# XML validation
./validate-xml.sh *.xhtml

# EPUB validation  
./validate-epub.sh

# Grammar analysis (all files)
python3 validate-grammar.py --all

# Fact-checking (specific file)
python3 validate-facts.py 44-bibliography.xhtml
```

## Interpreting Results

### Validation Status Codes
- **0**: All validations passed
- **1**: One or more validations failed
- **Exit codes accumulate**: Total failures = XML + EPUB + Spelling + Grammar + Facts

### Common Issues and Solutions

#### Spelling Validation
- **High error counts**: Review `aspell-personal.txt` and add specialized terms
- **False positives**: Update personal dictionary with domain-specific vocabulary
- **HTML artifacts**: Check text extraction logic for entities

#### Grammar Validation
- **LanguageTool network errors**: Tool gracefully degrades to readability analysis only
- **High complexity scores**: Consider simplifying sentences for target audience
- **Grade level mismatches**: Review content complexity against intended readability

#### Fact-Checking
- **URL accessibility failures**: May be temporary; manually verify important links
- **Over-identification**: Review pattern matching for false positives
- **Bibliography issues**: Ensure consistent citation formatting

## Integration Workflows

### Development Workflow
1. **Pre-commit**: Run `./validate-all.sh --xml-only` for quick checks
2. **Content review**: Use `./validate-all.sh --spelling-only --grammar-only`
3. **Final validation**: Full `./validate-all.sh` before publishing

### Continuous Integration
```yaml
name: EPUB Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y xmlstarlet tidy aspell hunspell
          pip3 install language-tool-python textstat beautifulsoup4 requests
      - name: Run validation
        run: ./validate-all.sh
      - name: Upload reports
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: validation-reports
          path: validation_reports_*/
```

### Publishing Checklist
- [ ] All XHTML files pass XML validation
- [ ] EPUB file passes EPUBCheck with zero errors
- [ ] Spelling errors reviewed and addressed
- [ ] Grammar issues evaluated for target audience
- [ ] Bibliography URLs verified as accessible
- [ ] Factual claims reviewed for accuracy

## Customization

### Adding Specialized Terms
Edit `aspell-personal.txt`:
```
personal_ws-1.1 en 200
hairstyling
DevaCurl
SMART
mentorship
[additional terms...]
```

### Grammar Tool Configuration
Modify patterns in `validate-grammar.py`:
```python
# Custom patterns for domain-specific validation
custom_patterns = [
    r'\b(?:specific|terms|patterns)\b',
    # Add patterns as needed
]
```

### Fact-Checking Customization
Update patterns in `validate-facts.py`:
```python
# Customize factual claim detection
self.fact_patterns = [
    r'\b\d{4}\b',  # Years
    r'\b\d+%\b',   # Percentages
    # Add custom patterns
]
```

## Performance Considerations

### Processing Times (Approximate)
- **XML validation**: < 1 minute for all files
- **EPUB validation**: < 30 seconds
- **Spelling validation**: 2-5 minutes for all files
- **Grammar validation**: 5-15 minutes (depends on LanguageTool)
- **Fact-checking**: 2-5 minutes (depends on URL response times)

### Optimization Tips
1. Use individual validation options for faster iteration
2. Run grammar validation separately for detailed analysis
3. Cache validation results between minor content changes
4. Use parallel processing for large content sets

## Troubleshooting

### Common Installation Issues
```bash
# Missing XML tools
sudo apt-get install xmlstarlet tidy-html5

# Missing Python packages
pip3 install language-tool-python textstat beautifulsoup4 requests

# Missing spell checkers
sudo apt-get install aspell hunspell
```

### Permission Issues
```bash
# Make scripts executable
chmod +x validate-*.sh validate-*.py
```

### Java/EPUBCheck Issues
```bash
# Check Java installation
java -version

# Verify EPUBCheck path
ls -la epubcheck-4.2.6/epubcheck.jar
```

## Future Enhancements

### Planned Features
1. **Parallel processing**: Speed up validation with concurrent execution
2. **Interactive mode**: Allow real-time correction of issues
3. **Plugin system**: Extensible validation modules
4. **Integration APIs**: RESTful services for external tool integration
5. **Enhanced reporting**: HTML reports with interactive navigation

### MCP Tool Integration
See `mcp-tools-recommendations.md` for comprehensive MCP server implementation guidelines that enable:
- Real-time validation during editing
- Automated corrections and suggestions
- Integration with development workflows
- Publishing platform automation

---

## Conclusion

This validation system provides comprehensive quality assurance for EPUB development, ensuring both technical compliance and content quality. The modular design allows for flexible usage patterns while maintaining thorough validation coverage.

Regular use of these tools during development significantly reduces publishing issues and improves overall content quality.