# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an EPUB book project for "Curls & Contemplation: A Stylist's Interactive Journey Journal" by MD Warren. The repository contains the complete source files for generating a professional EPUB 3.2 book optimized for KDP and Apple Books platforms.

## Architecture

### File Structure
The project follows EPUB 3.2 standards with a flat file structure containing:
- **XHTML files** (1-44): Book content including chapters, front/back matter, worksheets and quizzes
- **CSS files**: `style.css` (main styles) and `fonts.css` (font definitions)
- **Font assets**: WOFF2 format fonts (Libre Baskerville, Cinzel Decorative, Montserrat)
- **Images**: JPEG/PNG assets for chapter quotes, decorative elements, and graphics
- **Configuration**: `book-map.yaml` (EPUB build configuration)

### Content Organization
- **Front Matter**: Title page, copyright, table of contents, dedication, self-assessments
- **16 Chapters**: Each following ACISS layout (title page → body → quiz → worksheet → closing image)
- **Back Matter**: Conclusion, answer key, multiple worksheets, author info, bibliography

### Template System (ACISS Layout)
Each chapter uses a consistent 5-section structure:
1. **Title Page**: Roman numeral in pill, stacked title with vertical bar, Bible quote, introduction with drop cap
2. **Body Content**: Main chapter text with semantic HTML and content styling
3. **Quiz**: Maximum 4 multiple choice questions (no answer keys in chapters)
4. **Worksheet**: Interactive journaling pages with prompts
5. **Closing Image**: Chapter-specific quote image

## Key Technical Details

### CSS Architecture
- Uses CSS custom properties for consistent theming
- Responsive design with mobile-first approach
- WCAG 2.2 AA accessibility compliance
- Print optimization for KDP
- Specialized classes for content types: `.case-study`, `.action-steps`, `.key-takeaways`, `.reflection-questions`

### EPUB Standards
- EPUB 3.2 compliant markup
- External CSS linking (production) vs embedded CSS (review)
- Semantic HTML with ARIA labels and roles
- Font embedding with relative paths (`../fonts/`, `../images/`, `../styles/`)

### File Naming Convention
Files use numeric prefixes (01-44) for ordering, not matching chapter numbers. Keep author's original filenames when editing.

## Common Development Tasks

### Validation and QA
```bash
# EPUB validation (requires epubcheck)
epubcheck book.epub

# CSS validation
# Use W3C CSS Validator or built-in tools

# Accessibility check
# Use WAVE, axe, or similar tools for WCAG 2.2 AA compliance
```

### Content Editing Guidelines
- Preserve all content exactly - no rewriting or adding facts
- Use semantic HTML markup with appropriate ARIA labels
- Maintain consistent CSS class usage per template type
- Keep external CSS links: `<link rel="stylesheet" type="text/css" href="../styles/fonts.css" />` followed by `style.css`
- Maximum 4 quiz questions per chapter with no answer keys embedded

### Asset Management
- Images must be optimized for EPUB (no base64 embedding in production)
- Font files are WOFF2 format only
- All paths use relative references from XHTML location
- Chapter images follow pattern: `chapter-{roman-numeral}-quote.JPEG`

## Build Configuration
The `book-map.yaml` file contains comprehensive build settings including:
- Metadata and ISBN information
- File processing order and templates
- Validation requirements
- Distribution platform settings
- Quality check parameters

## Accessibility Requirements
- WCAG 2.2 Level AA compliance
- High contrast design with tested color ratios
- Keyboard navigation support
- Screen reader compatibility
- Descriptive alt text for all images
- Semantic heading structure

## Important Notes
- Never inline CSS in production EPUB files
- Avoid smart quotes in markup
- Maintain page break controls for print versions
- Test across multiple EPUB readers for compatibility
- Preserve author's original content without modifications