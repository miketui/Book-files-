# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This repository contains the complete source files for **"Curls & Contemplation: A Stylist's Interactive Journey Journal"** by MD Warren - a professional EPUB 3.2 book project targeting KDP and Apple Books platforms.

**Key Technical Details:**
- **EPUB Version**: 3.2 compliant with semantic markup
- **Accessibility**: WCAG 2.2 Level AA compliance
- **Template System**: ACISS layout (Title Page → Body → Quiz → Worksheet → Closing Image)
- **Architecture**: External CSS with relative paths, WOFF2 font embedding
- **Content**: 16 chapters with interactive worksheets and quizzes
- **Build Target**: Professional publishing platform requirements

The project follows a flat file structure with numbered prefixes for ordering (not matching chapter numbers) and uses external CSS linking for production builds.

## Directory Structure

```
Book-files-/
├── epub_fixer.py              # Main build/fix script
├── book-map.yaml              # EPUB build configuration
├── CLAUDE.md                  # Claude AI instructions
├── curls-and-contemplation.epub # Final EPUB output
├── epubcheck-4.2.6/           # Validation tools
│   └── epubcheck.jar          # EPUB validation
├── META-INF/
│   └── container.xml          # EPUB container manifest
├── OEBPS/                     # EPUB content directory
│   ├── content.opf            # EPUB manifest
│   ├── styles/                # CSS files
│   │   ├── fonts.css          # Font definitions
│   │   └── style.css          # Main stylesheet
│   ├── fonts/                 # WOFF2 font files
│   │   ├── librebaskerville-*.woff2
│   │   ├── Montserrat-*.woff2
│   │   └── CinzelDecorative.woff2
│   ├── images/                # Chapter quotes & assets
│   │   ├── chapter-i-quote.JPEG
│   │   ├── chapter-ii-quote.JPEG
│   │   └── ... (per chapter)
│   └── text/                  # XHTML chapter files
│       ├── 9-chapter-i-*.xhtml
│       ├── 10-chapter-ii-*.xhtml
│       └── ... (numbered sequence)
├── *.xhtml                    # Source XHTML files (root level)
└── *.JPEG, *.PNG, *.woff2     # Asset files (root level)
```

**Important**: File numbering (01-44) drives build order, not chapter numbers. Maintain author's original naming conventions.

## Quick-Start Build

```bash
# Install dependencies
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install lxml beautifulsoup4 pyyaml

# Run the comprehensive EPUB fixer
python epub_fixer.py

# Validate the generated EPUB
java -jar epubcheck-4.2.6/epubcheck.jar curls-and-contemplation.epub
```

**Expected Output:**
- `curls-and-contemplation.epub` in project root
- `OEBPS/` directory with organized structure
- Zero epubcheck errors for successful build

## Development Commands

### Build & Fix
```bash
# Run all fixes (recommended)
python epub_fixer.py

# The script performs:
# 1. Normalizes filenames and updates references
# 2. Fixes XHTML markup (entities, namespaces)
# 3. Corrects CSS and asset link paths
# 4. Populates quiz sections with placeholder content
# 5. Creates content.opf manifest
# 6. Generates final EPUB package
```

### Validation & Quality Assurance
```bash
# EPUB structural validation
java -jar epubcheck-4.2.6/epubcheck.jar curls-and-contemplation.epub

# CSS validation (external tool)
# Upload OEBPS/styles/style.css to https://jigsaw.w3.org/css-validator/

# YAML configuration validation
python -c "import yaml; yaml.safe_load(open('book-map.yaml'))"

# Manual accessibility check
# Use WAVE, axe, or similar tools on generated XHTML files
```

### Asset Management
```bash
# Check image sizes (should be < 1MB each)
find . -name "*.JPEG" -o -name "*.PNG" | xargs ls -lh

# Verify font files are WOFF2 format
file *.woff2

# Test CSS path resolution
grep -r "href=" *.xhtml | grep -E "(fonts|style)\.css"
```

## Architecture & Template System

### ACISS Chapter Layout
Each chapter follows a consistent 5-section structure:
1. **Title Page**: Roman numeral pill, stacked title with vertical bar, Bible quote box, introduction with drop cap
2. **Body Content**: Main text wrapped in `.content-area` div with semantic HTML
3. **Quiz Section**: Maximum 4 multiple choice questions (no embedded answers)
4. **Worksheet**: Interactive journaling pages with static form elements
5. **Closing Image**: Chapter-specific quote image (`chapter-{roman}-quote.JPEG`)

### CSS Architecture
- **External linking**: `../styles/fonts.css` → `../styles/style.css` order
- **Custom properties**: Extensive CSS variables for consistent theming
- **Responsive design**: Mobile-first with print optimization
- **Accessibility**: WCAG 2.2 AA compliant colors, focus indicators, ARIA labels
- **Content classes**: `.case-study`, `.action-steps`, `.key-takeaways`, `.reflection-questions`

### File Processing Rules
- Preserve all content exactly - no rewriting
- Use numeric prefixes for ordering (not chapter numbers)
- External CSS for production, embedded for review only
- Relative paths: `../styles/`, `../images/`, `../fonts/`
- No base64 image embedding in production

## Testing & Troubleshooting

### Common Issues & Solutions

**"fonts.css not found" errors:**
```bash
# Check CSS link order and paths
grep -n "fonts.css" *.xhtml
# Should be: href="../styles/fonts.css" before style.css
```

**EPUBcheck duplicate ID errors:**
```bash
# Re-run fixer to normalize IDs
python epub_fixer.py
```

**Large file size warnings:**
```bash
# Check image sizes
du -sh OEBPS/images/*.JPEG
# Compress images if > 1MB each
```

**Smart quotes in markup:**
```bash
# Fixer automatically converts to numeric entities
grep -r "&[lr]squo;" *.xhtml  # Should return nothing after fixing
```

**Accessibility violations:**
```bash
# Check for missing alt text
grep -r "<img" *.xhtml | grep -v "alt="
# Verify ARIA labels on interactive elements
grep -r "aria-label" *.xhtml
```

### Build Quality Checklist
- [ ] External CSS links in correct order (`fonts.css` first)
- [ ] ACISS title page structure present
- [ ] Content wrapped in `.content-area` div
- [ ] Quiz sections limited to 4 questions max
- [ ] Worksheet sections use static form elements
- [ ] Closing images use correct naming pattern
- [ ] EPUBcheck returns zero errors
- [ ] Accessibility compliance verified

## Build Configuration

The `book-map.yaml` file controls:
- **Metadata**: ISBN, author, publication details
- **File processing**: Input/output mappings and templates
- **Validation**: EPUBcheck, CSS validation, accessibility checks
- **Distribution**: Platform-specific settings (KDP, Apple Books, Ingram Spark)
- **Optimization**: Image compression, font optimization

Key sections:
- `files[]`: Processing order and template assignments
- `build.validation`: Quality check requirements
- `distribution.*`: Platform publishing settings

## Continuous Integration

### GitHub Actions Workflow (Future)

Example `.github/workflows/epub-build.yml` for automated building and validation:

```yaml path=null start=null
name: EPUB Build and Validation

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-validate:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install Python dependencies
      run: |
        pip install lxml beautifulsoup4 pyyaml
        
    - name: Install EPUBCheck
      run: |
        wget https://github.com/w3c/epubcheck/releases/download/v4.2.6/epubcheck-4.2.6.zip
        unzip epubcheck-4.2.6.zip
        
    - name: Run EPUB fixer
      run: python epub_fixer.py
      
    - name: Validate EPUB
      run: java -jar epubcheck-4.2.6/epubcheck.jar curls-and-contemplation.epub
      
    - name: Upload EPUB artifact
      uses: actions/upload-artifact@v3
      with:
        name: epub-build
        path: curls-and-contemplation.epub
        
    - name: Upload build logs
      uses: actions/upload-artifact@v3
      if: failure()
      with:
        name: build-logs
        path: '*.log'
```

**TODO**: Activate CI when repository is hosted on GitHub/GitLab.

## Contributing Workflow

When adding new content or making changes:

1. **Create feature branch:**
   ```bash
   git checkout -b feat/update-chapter-xvii
   ```

2. **Make changes to source files:**
   - Edit XHTML files directly for content changes
   - Modify CSS for styling updates
   - Update `book-map.yaml` for structural changes

3. **Run build and validation:**
   ```bash
   python epub_fixer.py
   java -jar epubcheck-4.2.6/epubcheck.jar curls-and-contemplation.epub
   ```

4. **Test accessibility:**
   - Verify WCAG 2.2 AA compliance
   - Test with screen reader if possible
   - Check color contrast ratios

5. **Commit and push:**
   ```bash
   git add .
   git commit -m "feat: describe your changes"
   git push origin feat/update-chapter-xvii
   ```

## Reference Links

- [EPUB 3.2 Specification](https://w3c.github.io/publ-epub-revision/epub32/spec/)
- [WCAG 2.2 Guidelines](https://www.w3.org/WAI/WCAG22/quickref/)
- [EPUBCheck Tool](https://github.com/w3c/epubcheck)
- [W3C CSS Validator](https://jigsaw.w3.org/css-validator/)
- [KDP Publishing Guidelines](https://kdp.amazon.com/en_US/help/topic/G200634390)
- [Apple Books Asset Guide](https://help.apple.com/itc/booksassetguide/)

## Notes for AI Assistants

When working with this project:

1. **Never modify content**: Preserve author's exact wording and facts
2. **Maintain file naming**: Keep numeric prefixes and author's naming convention
3. **Respect template structure**: Follow ACISS layout requirements
4. **Use external CSS**: Never inline styles in production XHTML
5. **Validate thoroughly**: Run epubcheck and accessibility checks
6. **Preserve accessibility**: Maintain WCAG 2.2 AA compliance
7. **Test across readers**: Verify compatibility with major EPUB readers

The `epub_fixer.py` script handles most common issues automatically. Run it whenever making structural changes to ensure consistency and compliance.
