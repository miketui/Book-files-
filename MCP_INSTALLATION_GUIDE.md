# MCP Tools Installation Guide for EPUB Validation

This guide provides comprehensive MCP (Model Context Protocol) tools and recommendations for validating, linting, compiling, and performing grammar/spelling/fact checks on your "Curls & Contemplation" EPUB project.

## 🛠️ Available MCP Tools

### 1. Core Validation Tools (Already Installed)

#### Python-Based Validation Suite
- **`mcp_validation_tools.py`** - Comprehensive EPUB validation toolkit
- **`mcp_advanced_analysis.py`** - Fact-checking and content analysis
- **`epub_fixer.py`** - Existing structural fixes
- **`validate-xml.sh`** - XML validation script (requires dependencies)
- **`validate-epub.sh`** - EPUB validation script

## 🚀 Quick Start - Run All Validations

```bash
# Run comprehensive validation
python3 mcp_validation_tools.py

# Run advanced content analysis
python3 mcp_advanced_analysis.py

# Run EPUB structural fixes
python3 epub_fixer.py
```

## 📦 Recommended MCP Tool Installations

### For Enhanced XML/HTML Validation:

```bash
# System packages (if you have sudo access)
sudo apt update
sudo apt install -y xmlstarlet tidy hunspell hunspell-en-us aspell aspell-en

# Python packages for validation
pip3 install --user lxml beautifulsoup4 html5lib
```

### For Advanced Spelling & Grammar:

```bash
# Python-based spell checking
pip3 install --user pyspellchecker textstat

# Language Tool (advanced grammar checking)
pip3 install --user language-tool-python

# For enhanced text analysis
pip3 install --user nltk textblob
```

### For Content Quality Analysis:

```bash
# Readability and text analysis
pip3 install --user readability textstat prose-md

# For fact-checking and citation analysis
pip3 install --user scholarly requests beautifulsoup4
```

## 🔧 MCP Tool Categories & Use Cases

### 1. **XML/XHTML Validation & Linting**

**What it does:** Validates markup structure, checks XHTML compliance, ensures proper tag closure and namespaces.

**MCP Tools to install:**
```bash
# System tools
xmlstarlet  # XML manipulation and validation
tidy        # HTML/XHTML validation and formatting

# Python alternatives
pip3 install --user lxml html5lib
```

**Usage:**
```bash
# Using existing script (after installing dependencies)
./validate-xml.sh *.xhtml

# Using Python tool
python3 mcp_validation_tools.py
```

### 2. **Spelling & Grammar Checking**

**What it does:** Checks spelling accuracy, identifies grammar issues, suggests improvements.

**MCP Tools to install:**
```bash
# System spell checkers
hunspell hunspell-en-us  # Advanced spell checking
aspell aspell-en         # Alternative spell checker

# Python spell checkers
pip3 install --user pyspellchecker
pip3 install --user language-tool-python  # Advanced grammar checking
```

**Usage:**
```bash
# Built into the validation tools
python3 mcp_validation_tools.py  # Includes basic spelling/grammar

# For advanced grammar checking
python3 -c "
from language_tool_python import LanguageTool
tool = LanguageTool('en-US')
# Check your text files
"
```

### 3. **EPUB Compilation & Structure Validation**

**What it does:** Validates EPUB structure, checks file organization, runs EPUBCheck.

**MCP Tools (already available):**
- EPUBCheck (Java-based, already in project)
- Python validation suite
- Structural compliance checking

**Usage:**
```bash
# Run EPUBCheck validation
java -jar epubcheck-4.2.6/epubcheck.jar curls-and-contemplation.epub

# Or use the validation script
./validate-epub.sh

# Python-based structural validation
python3 mcp_validation_tools.py
```

### 4. **Fact-Checking & Content Analysis**

**What it does:** Verifies technical accuracy, checks for consistency, suggests citations.

**MCP Tools to install:**
```bash
# For web research and fact-checking
pip3 install --user requests beautifulsoup4
pip3 install --user scholarly  # Academic paper search

# For content analysis
pip3 install --user textstat nltk
```

**Usage:**
```bash
# Advanced content analysis
python3 mcp_advanced_analysis.py
```

### 5. **Accessibility Compliance**

**What it does:** Checks WCAG 2.2 AA compliance, validates alt text, tests color contrast.

**MCP Tools to install:**
```bash
# Python accessibility tools
pip3 install --user axe-core-python
pip3 install --user accessibility-checker

# For color contrast testing
pip3 install --user colour-science
```

**Usage:**
Built into the validation suite with accessibility checking capabilities.

## 🎯 Complete MCP Setup Commands

### Minimal Setup (Python-only):
```bash
cd /path/to/Book-files-
pip3 install --user lxml beautifulsoup4 html5lib pyspellchecker textstat
python3 mcp_validation_tools.py
```

### Full Setup (requires system admin):
```bash
# System packages
sudo apt update
sudo apt install -y xmlstarlet tidy hunspell hunspell-en-us aspell aspell-en

# Python packages
pip3 install --user lxml beautifulsoup4 html5lib pyspellchecker language-tool-python textstat nltk

# Run full validation
python3 mcp_validation_tools.py
python3 mcp_advanced_analysis.py
```

### Docker/Container Setup:
```dockerfile
FROM ubuntu:24.04
RUN apt update && apt install -y \
    python3 python3-pip \
    xmlstarlet tidy \
    hunspell hunspell-en-us \
    aspell aspell-en \
    openjdk-17-jre

RUN pip3 install lxml beautifulsoup4 html5lib pyspellchecker language-tool-python textstat

WORKDIR /epub-project
COPY . .
CMD ["python3", "mcp_validation_tools.py"]
```

## 📋 Validation Workflow

### Step 1: Structural Fixes
```bash
python3 epub_fixer.py  # Fix known structural issues
```

### Step 2: Comprehensive Validation
```bash
python3 mcp_validation_tools.py  # XML, spelling, structure validation
```

### Step 3: Advanced Analysis
```bash
python3 mcp_advanced_analysis.py  # Fact-checking, content quality
```

### Step 4: EPUB Compilation Check
```bash
java -jar epubcheck-4.2.6/epubcheck.jar curls-and-contemplation.epub
```

### Step 5: Review Reports
- `mcp_validation_report.json` - Comprehensive validation results
- `mcp_advanced_analysis.json` - Content analysis results

## 🔍 What Each Tool Validates

### XML/XHTML Validation:
- ✅ Well-formed XML structure
- ✅ XHTML namespace declarations
- ✅ Proper tag closure
- ✅ DOCTYPE declarations
- ✅ Entity encoding

### Content Quality:
- ✅ Spelling accuracy
- ✅ Basic grammar checking
- ✅ Sentence length analysis
- ✅ Vocabulary consistency
- ✅ Repetitive word usage

### EPUB Structure:
- ✅ CSS link order (fonts.css before style.css)
- ✅ ACISS template compliance
- ✅ Content area wrappers
- ✅ Quiz and worksheet sections
- ✅ External CSS (no inline styles)

### Content Analysis:
- ✅ Technical accuracy in beauty/styling content
- ✅ Citation requirements for claims
- ✅ Terminology consistency
- ✅ Accessibility compliance
- ✅ Link validation

### File Management:
- ✅ Image file sizes (< 1MB recommended)
- ✅ EPUB file size optimization
- ✅ Asset organization
- ✅ Font embedding

## 📊 Expected Output

After running the MCP tools, you'll get:

1. **Console Output**: Real-time validation feedback
2. **JSON Reports**: Detailed analysis data
3. **Pass/Fail Status**: Clear indication of project readiness
4. **Fix Recommendations**: Specific suggestions for improvements

## 🎉 Next Steps

1. **Install the MCP tools** based on your system capabilities
2. **Run the validation suite** to identify current issues  
3. **Address critical errors** before proceeding to publication
4. **Review warnings** and apply fixes as appropriate
5. **Re-run validation** to confirm fixes
6. **Generate final EPUB** and validate with EPUBCheck

## 💡 Pro Tips

- **Run validations frequently** during development
- **Fix errors in batches** by category
- **Keep backup copies** before making bulk changes
- **Test EPUB files** in multiple readers after validation
- **Use version control** to track changes and fixes

## 🆘 Troubleshooting

**Common Issues:**

1. **Missing dependencies**: Install system packages with package manager
2. **Python module errors**: Use `pip3 install --user` for user-space installation
3. **Java not found**: Install OpenJDK for EPUBCheck validation
4. **Permission errors**: Use `--user` flag with pip or adjust file permissions

**Getting Help:**
- Check error logs in the JSON reports
- Run individual tools to isolate issues
- Use `python3 -m pip install --user <package>` for installation problems