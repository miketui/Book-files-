# EPUB Interior Playbook — Chapters Only
**Canonical template = Chapter 1** (hardcoded structure, classes, and assets)

This guide converts every Markdown chapter in **Ty.zip** into:
1) **Publishable, CSS‑styled, EPUB‑ready XHTML**, and  
2) a **React “Canvas” preview** for visual QA.

> Scope: chapters only (no front‑matter/back‑matter, no EPUB packaging yet).

---

## 1) Folder Tree (chapters-only)

```
/OEBPS
  /chapters_src/              ← your Markdown (.md) with YAML front‑matter
  /chapters/                  ← OUTPUT: .xhtml per chapter
  /images/                    ← brushstroke + closing quote images + decor
  /styles/                    ← fonts.css, style.css
  /fonts/                     ← .woff2 files referenced by fonts.css
  /templates/                 ← canonical templates
    chapter-template.xhtml    ← Chapter 1 XHTML template (ACISS layout)
    ChapterCanvas.jsx         ← React preview template
  book-map.yaml               ← order + roman + closing image map
  project-structure.yaml
/tools
  md-to-xhtml.js              ← convert one .md → .xhtml (optional helper)
  make-canvas.js              ← render React Canvas preview (optional)
  qa-xhtml.js                 ← run QA checks (optional)
```

**External paths used inside XHTML (must match exactly):**
- CSS: `../styles/fonts.css`, `../styles/style.css`
- IMAGES: `../images/<asset>`

Core decorative images (keep *exact casing* as in Ty.zip):  
`brushstroke.JPEG`, `quote-marks.PNG`, `decorative-line.JPEG`, `endnote-marker.PNG`, `quiz-checkbox.PNG`, per‑chapter `chapter-*.JPEG` quote images.

---

## 2) Chapter 1 = Canon (what every chapter must look like)

- **Centered brushstroke** with **Roman badge** on top
- **Stacked title** (one word per line) with **left vertical accent bar**
- **Bible quote callout** (epigraph)
- **“Introduction”** label + **drop‑cap** first intro paragraph
- **Body** (lossless Markdown → HTML)
- **Endnotes**, then **Quiz**, **Worksheet**
- **Closing image quote**

Order is fixed: **Title Page → Body → Endnotes → Quiz → Worksheet → Closing Image**.

---

## 3) YAML front‑matter → XHTML

```yaml
title: "Chapter I: Unveiling Your Creative Odyssey"
chapter_number: I
author: "Michael Garrett"
image_quote: "../assets/images/chapter-i-quote.png"
```
- `chapter_number` → Roman badge text
- `title` → split into stacked `<h1 class="chapter-title-word">` lines
- `image_quote` → normalize path to `/OEBPS/images/chapter-i-quote.JPEG`

Other keys (word_count, reading_time, tags, etc.) are metadata only.

---

## 4) Canonical XHTML skeleton (copy, then fill)

Link to `/OEBPS/templates/chapter-template.xhtml` and replace placeholders: Roman, TitleStack, epigraph, introduction paragraphs, Body HTML, Quiz, Worksheet, Endnotes, Closing Image.

> **All CSS and images must remain relative** (no inline CSS).

---

## 5) Markdown → XHTML (lossless rules)

- `#` (top) → **title page only** (do not repeat in body)
- `##` → `<h2>`, `###` → `<h3>`, `####` → `<h4>`
- Paragraphs → `<p>` (preserve emphasis/links)
- Lists → semantic `<ul>`/`<ol>`
- First top‑level blockquote → **epigraph** on title page; others stay `<blockquote>` in body
- Tables → `<table><thead><tbody>`
- Images → `<img src="../images/...">` with **non‑empty** `alt`
- Footnotes:
  - Inline `[^n]` → `<sup id="fnref-n"><a href="#fn-n">n</a></sup>`
  - Master list → `<section class="footnotes footnotes-end-of-document" role="doc-endnotes">`
  - If mimicking Chapter 1’s short list, keep optional `<aside class="endnotes">` too
  - Ids must pair (`fn-n` ↔ `fnref-n`) + backlink class `footnote-back`
- Special blocks:
  - “Actionable Steps” →
    ```html
    <div class="action-steps">
      <h2>Actionable Steps</h2>
      <ol>…</ol>
    </div>
    ```
  - Case study → `<div class="case-study">…</div>`

---

## 6) Closing image quote (per chapter)

Map in `book-map.yaml`:
```yaml
chapters:
  - file: "09-Chapter-I-Unveiling-Your-Creative-Odyssey.xhtml"
    roman: "I"
    quote_image: "chapter-i-quote.JPEG"
```
Then, in XHTML:
```html
<section class="image-quote" role="group" aria-labelledby="closing-caption">
  <figure>
    <img src="../images/chapter-i-quote.JPEG" alt="Closing quote image for Chapter I" />
    <figcaption id="closing-caption" class="font-small color-light">[caption text]</figcaption>
  </figure>
</section>
```

---

## 7) React “Canvas” preview (QA only)

`/OEBPS/templates/ChapterCanvas.jsx` should mirror XHTML structure/classes and import assets via the same relative paths. No copy changes; purely visual check.

---

## 8) QA Checklist (each chapter)

- [ ] CSS paths exactly `../styles/fonts.css` + `../styles/style.css`
- [ ] Brushstroke present, Roman centered
- [ ] `.chapter-title-vertical` present (vertical accent bar)
- [ ] Title split into stacked `<h1>` lines
- [ ] Epigraph card present (blockquote + figcaption)
- [ ] “Introduction” heading + drop‑cap first paragraph
- [ ] Headings in order (h2→h3→h4), no rank skips
- [ ] Footnotes resolved; master endnotes section present if refs exist
- [ ] Quiz (≤ 4 Qs) matches format
- [ ] Worksheet block present
- [ ] Closing image file name matches `book-map.yaml` and exists in `/images`
- [ ] No inline CSS (except minimal worksheet input height if needed)
- [ ] No copy edits; 1:1 with Markdown

---

## 9) How the converter “knows” to use Chapter 1

The converter **always** starts from `/OEBPS/templates/chapter-template.xhtml` (Chapter 1). It reads YAML for `chapter_number`, splits `title` into TitleStack, lifts the first blockquote as the epigraph, flows intro paragraphs into the Introduction block, converts remaining Markdown to body HTML, then appends quiz/worksheet/closing image according to `book-map.yaml`. This guarantees all chapters look like Chapter 1 while keeping their own content **word‑for‑word**.

---

## 10) Not packaging yet

Front/back matter and EPUB packaging (`content.opf`, `toc.xhtml`, `.epub`) are deferred until your other sections are ready.
