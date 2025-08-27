#!/usr/bin/env python3
"""
EPUB Fixer Script for Curls & Contemplation
Systematically fixes all issues in the EPUB project
"""

import os
import re
import shutil
import yaml
from pathlib import Path
from lxml import etree, html
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EPUBFixer:
    def __init__(self, project_dir):
        self.project_dir = Path(project_dir)
        self.fixes_log = []
        
    def log_fix(self, filename, change):
        """Log a fix that was made"""
        self.fixes_log.append(f"{filename}: {change}")
        logger.info(f"Fixed {filename}: {change}")
        
    def normalize_filename(self, filename):
        """Normalize filename to lowercase with hyphens, removing _final and spaces"""
        # Remove _final suffix
        name = filename.replace('_final', '')
        
        # Convert to lowercase
        name = name.lower()
        
        # Replace spaces with hyphens
        name = name.replace(' ', '-')
        
        # Remove multiple consecutive hyphens
        name = re.sub('-+', '-', name)
        
        # Specific fixes for known problematic files
        name = name.replace('continuedlearningcommitment-2', 'continued-learning-commitment')
        name = name.replace('affirmationsclose', 'affirmations-close')
        name = name.replace('selfcarejournal', 'self-care-journal')
        name = name.replace('journalpage', 'journal-page')
        name = name.replace('professionaldevelopment', 'professional-development')
        name = name.replace('affirmationodyssey', 'affirmation-odyssey')
        
        return name
    
    def rename_files_and_update_references(self):
        """Step 1: Normalize all filenames and update references"""
        logger.info("Step 1: Normalizing filenames and updating references...")
        
        # Get all XHTML files
        xhtml_files = list(self.project_dir.glob('*.xhtml'))
        rename_map = {}
        
        # Create rename mapping
        for file_path in xhtml_files:
            old_name = file_path.name
            new_name = self.normalize_filename(old_name)
            
            if old_name != new_name:
                rename_map[old_name] = new_name
                
        # Rename files
        for old_name, new_name in rename_map.items():
            old_path = self.project_dir / old_name
            new_path = self.project_dir / new_name
            
            if old_path.exists():
                shutil.move(old_path, new_path)
                self.log_fix(old_name, f"Renamed to {new_name}")
                
        # Update Table of Contents references
        toc_file = self.project_dir / '3-tableofcontents.xhtml'
        if toc_file.exists():
            self.update_toc_references(toc_file, rename_map)
            
        # Update book-map.yaml references
        book_map_file = self.project_dir / 'book-map.yaml'
        if book_map_file.exists():
            self.update_book_map_references(book_map_file, rename_map)
            
        return rename_map
    
    def update_toc_references(self, toc_file, rename_map):
        """Update Table of Contents with new filenames"""
        try:
            with open(toc_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Update href attributes
            for old_name, new_name in rename_map.items():
                content = content.replace(f'href="{old_name}"', f'href="{new_name}"')
                content = content.replace(f"href='{old_name}'", f"href='{new_name}'")
                
            with open(toc_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.log_fix('3-tableofcontents.xhtml', 'Updated file references')
        except Exception as e:
            logger.error(f"Error updating TOC: {e}")
    
    def update_book_map_references(self, book_map_file, rename_map):
        """Update book-map.yaml with new filenames"""
        try:
            with open(book_map_file, 'r', encoding='utf-8') as f:
                book_map = yaml.safe_load(f)
                
            # Update file references in the files section
            if 'files' in book_map:
                for file_entry in book_map['files']:
                    if 'input' in file_entry and file_entry['input'] in rename_map:
                        old_input = file_entry['input']
                        file_entry['input'] = rename_map[old_input]
                        self.log_fix('book-map.yaml', f'Updated {old_input} to {rename_map[old_input]}')
                        
                    if 'output' in file_entry:
                        # Update output paths to match OEBPS structure
                        output_path = file_entry['output']
                        filename = Path(output_path).name
                        if filename in rename_map:
                            file_entry['output'] = f"OEBPS/text/{rename_map[filename]}"
                            
            with open(book_map_file, 'w', encoding='utf-8') as f:
                yaml.dump(book_map, f, default_flow_style=False)
                
        except Exception as e:
            logger.error(f"Error updating book-map.yaml: {e}")
    
    def fix_xhtml_markup(self):
        """Step 2: Fix XHTML markup issues"""
        logger.info("Step 2: Fixing XHTML markup issues...")
        
        xhtml_files = list(self.project_dir.glob('*.xhtml'))
        
        for file_path in xhtml_files:
            self.fix_single_xhtml_file(file_path)
    
    def fix_single_xhtml_file(self, file_path):
        """Fix markup issues in a single XHTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Fix named entities
            entity_fixes = {
                '&nbsp;': '&#160;',
                '&mdash;': '&#8212;',
                '&ndash;': '&#8211;',
                '&ldquo;': '&#8220;',
                '&rdquo;': '&#8221;',
                '&lsquo;': '&#8216;',
                '&rsquo;': '&#8217;',
                '&hellip;': '&#8230;',
            }
            
            for entity, numeric in entity_fixes.items():
                if entity in content:
                    content = content.replace(entity, numeric)
                    self.log_fix(file_path.name, f'Replaced {entity} with {numeric}')
            
            # Ensure proper namespace declarations
            if '<html' in content and 'xmlns="http://www.w3.org/1999/xhtml"' not in content:
                content = content.replace('<html', '<html xmlns="http://www.w3.org/1999/xhtml"')
                self.log_fix(file_path.name, 'Added XHTML namespace')
                
            if '<html' in content and 'xmlns:epub="http://www.idpf.org/2007/ops"' not in content and 'epub:' in content:
                content = re.sub(r'<html([^>]*?)>', r'<html\1 xmlns:epub="http://www.idpf.org/2007/ops">', content)
                self.log_fix(file_path.name, 'Added EPUB namespace')
            
            # Fix self-closing tags that shouldn't be self-closing
            content = re.sub(r'<(div|p|h[1-6]|span|a)\s([^>]*?)\/>', r'<\1 \2></\1>', content)
            
            # Write back if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
        except Exception as e:
            logger.error(f"Error fixing {file_path}: {e}")
    
    def fix_css_and_asset_links(self):
        """Step 3: Fix CSS and asset link paths"""
        logger.info("Step 3: Fixing CSS and asset links...")
        
        xhtml_files = list(self.project_dir.glob('*.xhtml'))
        
        for file_path in xhtml_files:
            self.fix_css_links_in_file(file_path)
    
    def fix_css_links_in_file(self, file_path):
        """Fix CSS links in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Fix CSS links to use proper relative paths
            css_fixes = [
                (r'href=["\']fonts\.css["\']', 'href="../styles/fonts.css"'),
                (r'href=["\']style\.css["\']', 'href="../styles/style.css"'),
                (r'href=["\']\.\.\/fonts\.css["\']', 'href="../styles/fonts.css"'),
                (r'href=["\']\.\.\/style\.css["\']', 'href="../styles/style.css"'),
            ]
            
            for pattern, replacement in css_fixes:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    self.log_fix(file_path.name, f'Fixed CSS path: {replacement}')
            
            # Ensure fonts.css comes before style.css
            font_css = '<link rel="stylesheet" type="text/css" href="../styles/fonts.css" />'
            style_css = '<link rel="stylesheet" type="text/css" href="../styles/style.css" />'
            
            if font_css in content and style_css in content:
                # Remove existing links
                content = content.replace(font_css, '')
                content = content.replace(style_css, '')
                
                # Insert both in correct order in head
                head_pattern = r'(</title>.*?)(</head>)'
                replacement = r'\1\n    ' + font_css + '\n    ' + style_css + r'\n  \2'
                content = re.sub(head_pattern, replacement, content, flags=re.DOTALL)
            
            # Write back if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
        except Exception as e:
            logger.error(f"Error fixing CSS links in {file_path}: {e}")
    
    def populate_quizzes(self):
        """Step 4: Populate quiz sections with placeholder content"""
        logger.info("Step 4: Populating quizzes...")
        
        # Find all chapter files (those containing "chapter" in the name)
        chapter_files = [f for f in self.project_dir.glob('*.xhtml') if 'chapter' in f.name.lower()]
        
        for file_path in chapter_files:
            self.populate_quiz_in_file(file_path)
    
    def populate_quiz_in_file(self, file_path):
        """Add quiz options to a chapter file if missing"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check if file has quiz section but missing options
            if 'quiz-options' in content and '<li>' not in content[content.find('quiz-options'):]:
                # Add placeholder quiz options
                placeholder_options = '''
                    <li><span class="opt-label">A.</span> Option A (placeholder)</li>
                    <li><span class="opt-label">B.</span> Option B (placeholder)</li>
                    <li><span class="opt-label">C.</span> Option C (placeholder)</li>
                    <li><span class="opt-label">D.</span> Option D (placeholder)</li>'''
                
                # Find quiz-options ul and add options
                pattern = r'(<ul class="quiz-options"[^>]*>)\s*(</ul>)'
                replacement = r'\1' + placeholder_options + r'\n                  \2'
                
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
                    self.log_fix(file_path.name, 'Added placeholder quiz options')
                    
        except Exception as e:
            logger.error(f"Error populating quiz in {file_path}: {e}")
    
    def create_content_opf(self):
        """Step 5: Create content.opf manifest file"""
        logger.info("Step 5: Creating content.opf...")
        
        try:
            # Load book-map.yaml for metadata
            book_map_file = self.project_dir / 'book-map.yaml'
            if book_map_file.exists():
                with open(book_map_file, 'r', encoding='utf-8') as f:
                    book_map = yaml.safe_load(f)
            else:
                book_map = {}
                
            # Create OEBPS directory structure
            oebps_dir = self.project_dir / 'OEBPS'
            oebps_dir.mkdir(exist_ok=True)
            (oebps_dir / 'text').mkdir(exist_ok=True)
            (oebps_dir / 'styles').mkdir(exist_ok=True)
            (oebps_dir / 'images').mkdir(exist_ok=True)
            (oebps_dir / 'fonts').mkdir(exist_ok=True)
            
            # Move files to OEBPS structure
            self.organize_epub_structure()
            
            # Create content.opf
            self.generate_content_opf(oebps_dir, book_map)
            
        except Exception as e:
            logger.error(f"Error creating content.opf: {e}")
    
    def organize_epub_structure(self):
        """Organize files into proper EPUB structure"""
        oebps_dir = self.project_dir / 'OEBPS'
        
        # Move XHTML files to text directory
        for xhtml_file in self.project_dir.glob('*.xhtml'):
            dest = oebps_dir / 'text' / xhtml_file.name
            if not dest.exists():
                shutil.copy2(xhtml_file, dest)
                
        # Move CSS files to styles directory
        for css_file in self.project_dir.glob('*.css'):
            dest = oebps_dir / 'styles' / css_file.name
            if not dest.exists():
                shutil.copy2(css_file, dest)
                
        # Move font files to fonts directory
        for font_file in self.project_dir.glob('*.woff2'):
            dest = oebps_dir / 'fonts' / font_file.name
            if not dest.exists():
                shutil.copy2(font_file, dest)
                
        # Move image files to images directory
        for img_ext in ['*.jpg', '*.jpeg', '*.png', '*.JPEG', '*.PNG']:
            for img_file in self.project_dir.glob(img_ext):
                dest = oebps_dir / 'images' / img_file.name
                if not dest.exists():
                    shutil.copy2(img_file, dest)
    
    def generate_content_opf(self, oebps_dir, book_map):
        """Generate the content.opf manifest file"""
        book_info = book_map.get('book', {})
        
        opf_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="BookId">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>{book_info.get('title', 'Curls & Contemplation')}</dc:title>
    <dc:creator>{book_info.get('author', 'MD Warren')}</dc:creator>
    <dc:identifier id="BookId">{book_info.get('identifier', {}).get('text', 'urn:uuid:9fa5e2ef-5fd8-4f5b-9077-0b9e856cda3d')}</dc:identifier>
    <dc:language>{book_info.get('language', 'en-US')}</dc:language>
    <dc:date>{book_info.get('date', '2025-01-27')}</dc:date>
    <dc:rights>{book_info.get('rights', '© 2025 MD Warren. All rights reserved.')}</dc:rights>
    <dc:publisher>{book_info.get('publisher', 'MD Warren')}</dc:publisher>
    <dc:subject>Beauty</dc:subject>
    <dc:subject>Business</dc:subject>
    <dc:subject>Personal Development</dc:subject>
    <dc:subject>Hairstyling</dc:subject>
    <meta property="dcterms:modified">2025-01-27T10:00:00Z</meta>
  </metadata>
  
  <manifest>'''
        
        # Add XHTML files to manifest
        text_files = sorted(list((oebps_dir / 'text').glob('*.xhtml')))
        for i, file_path in enumerate(text_files):
            file_id = f"text{i+1:03d}"
            opf_content += f'\n    <item id="{file_id}" href="text/{file_path.name}" media-type="application/xhtml+xml"/>'
            
        # Add CSS files
        css_files = list((oebps_dir / 'styles').glob('*.css'))
        for i, css_file in enumerate(css_files):
            opf_content += f'\n    <item id="css{i+1}" href="styles/{css_file.name}" media-type="text/css"/>'
            
        # Add font files
        font_files = list((oebps_dir / 'fonts').glob('*.woff2'))
        for i, font_file in enumerate(font_files):
            opf_content += f'\n    <item id="font{i+1}" href="fonts/{font_file.name}" media-type="font/woff2"/>'
            
        # Add image files
        img_files = list((oebps_dir / 'images').glob('*'))
        for i, img_file in enumerate(img_files):
            media_type = 'image/jpeg' if img_file.suffix.lower() in ['.jpg', '.jpeg'] else 'image/png'
            opf_content += f'\n    <item id="img{i+1}" href="images/{img_file.name}" media-type="{media_type}"/>'
            
        opf_content += '''
  </manifest>
  
  <spine>'''
        
        # Add spine items in reading order
        for i, file_path in enumerate(text_files):
            file_id = f"text{i+1:03d}"
            opf_content += f'\n    <itemref idref="{file_id}"/>'
            
        opf_content += '''
  </spine>
</package>'''
        
        # Write content.opf
        with open(oebps_dir / 'content.opf', 'w', encoding='utf-8') as f:
            f.write(opf_content)
            
        self.log_fix('content.opf', 'Created EPUB manifest file')
    
    def create_epub_package(self):
        """Step 6: Create final EPUB package"""
        logger.info("Step 6: Creating EPUB package...")
        
        try:
            import zipfile
            
            epub_file = self.project_dir / 'curls-and-contemplation.epub'
            oebps_dir = self.project_dir / 'OEBPS'
            
            # Create META-INF directory and container.xml
            meta_inf_dir = self.project_dir / 'META-INF'
            meta_inf_dir.mkdir(exist_ok=True)
            
            container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>'''
            
            with open(meta_inf_dir / 'container.xml', 'w', encoding='utf-8') as f:
                f.write(container_xml)
                
            # Create mimetype file
            with open(self.project_dir / 'mimetype', 'w', encoding='utf-8') as f:
                f.write('application/epub+zip')
            
            # Create ZIP file
            with zipfile.ZipFile(epub_file, 'w', zipfile.ZIP_DEFLATED) as epub_zip:
                # Add mimetype first (uncompressed)
                epub_zip.write(self.project_dir / 'mimetype', 'mimetype', compress_type=zipfile.ZIP_STORED)
                
                # Add META-INF files
                epub_zip.write(meta_inf_dir / 'container.xml', 'META-INF/container.xml')
                
                # Add OEBPS files
                for root, dirs, files in os.walk(oebps_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = str(file_path.relative_to(self.project_dir))
                        epub_zip.write(file_path, arcname)
                        
            self.log_fix('EPUB', f'Created package: {epub_file}')
            return epub_file
            
        except Exception as e:
            logger.error(f"Error creating EPUB package: {e}")
            return None
    
    def run_all_fixes(self):
        """Run all fixing steps in sequence"""
        logger.info("Starting comprehensive EPUB fixes...")
        
        try:
            # Step 1: Normalize filenames and update references
            rename_map = self.rename_files_and_update_references()
            
            # Step 2: Fix XHTML markup
            self.fix_xhtml_markup()
            
            # Step 3: Fix CSS and asset links
            self.fix_css_and_asset_links()
            
            # Step 4: Populate quizzes
            self.populate_quizzes()
            
            # Step 5: Create content.opf and organize structure
            self.create_content_opf()
            
            # Step 6: Create EPUB package
            epub_file = self.create_epub_package()
            
            # Print summary
            logger.info(f"EPUB fixes completed! Created: {epub_file}")
            logger.info(f"Total fixes applied: {len(self.fixes_log)}")
            
            return epub_file
            
        except Exception as e:
            logger.error(f"Error during EPUB fixing process: {e}")
            return None


if __name__ == "__main__":
    project_dir = "/Users/yurielyoung/Book-files-"
    fixer = EPUBFixer(project_dir)
    epub_file = fixer.run_all_fixes()
    
    if epub_file:
        print(f"\n✅ EPUB fixes completed successfully!")
        print(f"📚 Created: {epub_file}")
        print(f"🔧 Total fixes applied: {len(fixer.fixes_log)}")
        print("\nNext: Run epubcheck to validate the EPUB")
    else:
        print("❌ EPUB fixing failed. Check the logs above.")