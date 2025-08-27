#!/usr/bin/env python3
"""
Platform-Specific Guidelines Review
Check EPUB compliance with KDP, Apple Books, and other platform requirements
"""

import os
import zipfile
from pathlib import Path
from bs4 import BeautifulSoup
import re

class PlatformGuidelinesChecker:
    def __init__(self, epub_dir):
        self.epub_dir = Path(epub_dir)
        self.oebps_dir = self.epub_dir / 'OEBPS'
        self.epub_file = self.epub_dir / 'curls-and-contemplation.epub'
        self.issues = []
        self.warnings = []
        
    def check_all_platforms(self):
        """Check compliance with all major platform guidelines"""
        print("=== PLATFORM-SPECIFIC GUIDELINES REVIEW ===\\n")
        
        # Check KDP requirements
        self.check_kdp_requirements()
        
        # Check Apple Books requirements  
        self.check_apple_books_requirements()
        
        # Check general EPUB standards
        self.check_general_epub_standards()
        
        # Check common platform requirements
        self.check_common_requirements()
        
        print("\\n=== PLATFORM COMPLIANCE SUMMARY ===")
        print(f"Critical issues: {len(self.issues)}")
        print(f"Warnings: {len(self.warnings)}")
        
        return len(self.issues) == 0
        
    def check_kdp_requirements(self):
        """Check Kindle Direct Publishing specific requirements"""
        print("📚 KINDLE DIRECT PUBLISHING (KDP) REQUIREMENTS")
        print("-" * 50)
        
        # 1. No JavaScript
        js_files = list(self.oebps_dir.rglob('*.js'))
        if js_files:
            self.issues.append(f"KDP: JavaScript files found: {[f.name for f in js_files]}")
            print("  ❌ JavaScript files detected (not allowed on KDP)")
        else:
            print("  ✅ No JavaScript files found")
            
        # 2. Check for script tags in XHTML
        script_found = False
        for xhtml_file in self.oebps_dir.rglob('*.xhtml'):
            with open(xhtml_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if '<script' in content.lower():
                    script_found = True
                    self.issues.append(f"KDP: Script tags found in {xhtml_file.name}")
                    
        if script_found:
            print("  ❌ Script tags found in XHTML files")
        else:
            print("  ✅ No script tags in XHTML files")
            
        # 3. No video/audio files
        media_files = []
        for ext in ['*.mp4', '*.avi', '*.mov', '*.mp3', '*.wav', '*.ogg']:
            media_files.extend(list(self.oebps_dir.rglob(ext)))
            
        if media_files:
            self.issues.append(f"KDP: Media files found: {[f.name for f in media_files]}")
            print("  ❌ Video/audio files detected")
        else:
            print("  ✅ No video/audio files found")
            
        # 4. Check image sizes (recommend < 2MB each for KDP)
        large_images = []
        for img_file in self.oebps_dir.rglob('*.JPEG'):
            if img_file.stat().st_size > 2 * 1024 * 1024:  # 2MB
                large_images.append(f"{img_file.name} ({img_file.stat().st_size / 1024 / 1024:.1f}MB)")
                
        if large_images:
            self.warnings.append(f"KDP: Large images may cause issues: {large_images}")
            print(f"  ⚠️  Large images found (>2MB): {len(large_images)}")
        else:
            print("  ✅ All images under 2MB")
            
        # 5. Check EPUB file size (KDP recommends < 50MB)
        if self.epub_file.exists():
            epub_size = self.epub_file.stat().st_size / 1024 / 1024  # MB
            if epub_size > 50:
                self.warnings.append(f"KDP: EPUB file is {epub_size:.1f}MB (>50MB may have issues)")
                print(f"  ⚠️  Large EPUB file: {epub_size:.1f}MB")
            else:
                print(f"  ✅ EPUB file size acceptable: {epub_size:.1f}MB")
                
        print()
        
    def check_apple_books_requirements(self):
        """Check Apple Books specific requirements"""
        print("🍎 APPLE BOOKS REQUIREMENTS")
        print("-" * 50)
        
        # 1. Check for EPUB 3.2 compliance
        with open(self.oebps_dir / 'content.opf', 'r', encoding='utf-8') as f:
            opf_content = f.read()
            
        if 'version="3.0"' in opf_content:
            print("  ✅ EPUB 3.0+ version detected")
        else:
            self.issues.append("Apple Books: EPUB version should be 3.0 or higher")
            print("  ❌ EPUB version not 3.0+")
            
        # 2. Check accessibility features (Apple emphasizes these)
        accessibility_features = []
        sample_xhtml = self.oebps_dir / 'text' / '9-chapter-i-unveiling-your-creative-odyssey.xhtml'
        
        with open(sample_xhtml, 'r', encoding='utf-8') as f:
            content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Check for alt text
            imgs_without_alt = soup.find_all('img', alt=lambda x: x is None)
            if not imgs_without_alt:
                accessibility_features.append("alt text on images")
                
            # Check for ARIA labels
            if soup.find_all(attrs={'aria-label': True}):
                accessibility_features.append("ARIA labels")
                
            # Check for semantic markup
            if soup.find_all(['section', 'article', 'nav', 'aside']):
                accessibility_features.append("semantic HTML5")
                
        if accessibility_features:
            print(f"  ✅ Accessibility features present: {', '.join(accessibility_features)}")
        else:
            self.warnings.append("Apple Books: Limited accessibility features detected")
            print("  ⚠️  Limited accessibility features")
            
        # 3. Check font embedding (Apple supports WOFF2)
        woff2_fonts = list(self.oebps_dir.glob('fonts/*.woff2'))
        if woff2_fonts:
            print(f"  ✅ WOFF2 fonts embedded: {len(woff2_fonts)} files")
        else:
            self.warnings.append("Apple Books: No WOFF2 fonts found for consistent rendering")
            print("  ⚠️  No WOFF2 fonts found")
            
        # 4. Check for color profiles (Apple prefers RGB for screens)
        # This would require image analysis tools, so we'll skip for now
        print("  ⚠️  Color profile check skipped (requires ImageMagick)")
        
        print()
        
    def check_general_epub_standards(self):
        """Check general EPUB 3.2 standards"""
        print("📖 EPUB 3.2 STANDARDS COMPLIANCE")
        print("-" * 50)
        
        # 1. Check spine linear order
        with open(self.oebps_dir / 'content.opf', 'r', encoding='utf-8') as f:
            opf_content = f.read()
            
        # Look for linear="no" attributes
        if 'linear="no"' in opf_content:
            print("  ✅ Non-linear spine items properly marked")
        else:
            print("  ✅ All spine items linear (standard)")
            
        # 2. Check for required metadata
        required_metadata = ['dc:title', 'dc:creator', 'dc:identifier', 'dc:language']
        missing_metadata = []
        
        for meta in required_metadata:
            if meta not in opf_content:
                missing_metadata.append(meta)
                
        if missing_metadata:
            self.issues.append(f"EPUB: Missing required metadata: {missing_metadata}")
            print(f"  ❌ Missing metadata: {', '.join(missing_metadata)}")
        else:
            print("  ✅ All required metadata present")
            
        # 3. Check for proper namespace declarations
        sample_xhtml = self.oebps_dir / 'text' / '9-chapter-i-unveiling-your-creative-odyssey.xhtml'
        with open(sample_xhtml, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'xmlns="http://www.w3.org/1999/xhtml"' in content:
            print("  ✅ XHTML namespace properly declared")
        else:
            self.issues.append("EPUB: XHTML namespace not properly declared")
            print("  ❌ Missing XHTML namespace")
            
        print()
        
    def check_common_requirements(self):
        """Check requirements common to multiple platforms"""
        print("🌐 COMMON PLATFORM REQUIREMENTS")
        print("-" * 50)
        
        # 1. Check for cover image (most platforms require)
        cover_found = False
        
        # Check in content.opf for cover reference
        with open(self.oebps_dir / 'content.opf', 'r', encoding='utf-8') as f:
            opf_content = f.read()
            
        if 'properties="cover-image"' in opf_content:
            cover_found = True
            print("  ✅ Cover image referenced in manifest")
        else:
            # Look for common cover file names
            cover_files = list(self.oebps_dir.rglob('cover.*'))
            if cover_files:
                cover_found = True
                print(f"  ✅ Cover image file found: {cover_files[0].name}")
            
        if not cover_found:
            self.warnings.append("Common: No cover image detected")
            print("  ⚠️  No cover image found")
            
        # 2. Check for table of contents
        toc_files = list(self.oebps_dir.rglob('*toc*.xhtml')) + list(self.oebps_dir.rglob('*contents*.xhtml'))
        if toc_files:
            print(f"  ✅ Table of contents found: {toc_files[0].name}")
        else:
            self.warnings.append("Common: No table of contents detected")
            print("  ⚠️  No table of contents found")
            
        # 3. Check reading order integrity
        with open(self.oebps_dir / 'content.opf', 'r', encoding='utf-8') as f:
            opf_content = f.read()
            
        spine_items = re.findall(r'<itemref idref="([^"]+)"', opf_content)
        if len(spine_items) > 0:
            print(f"  ✅ Reading order defined: {len(spine_items)} items in spine")
        else:
            self.issues.append("Common: No reading order defined in spine")
            print("  ❌ No reading order defined")
            
        print()
        
    def save_report(self, output_file):
        """Save platform compliance report"""
        with open(output_file, 'w') as f:
            f.write("PLATFORM-SPECIFIC GUIDELINES REVIEW\\n")
            f.write("=" * 50 + "\\n\\n")
            
            if not self.issues and not self.warnings:
                f.write("✅ FULL PLATFORM COMPLIANCE\\n\\n")
                f.write("The EPUB meets requirements for:\\n")
                f.write("- Kindle Direct Publishing (KDP)\\n")
                f.write("- Apple Books\\n") 
                f.write("- EPUB 3.2 standards\\n")
                f.write("- Common platform requirements\\n")
            else:
                if self.issues:
                    f.write(f"❌ CRITICAL ISSUES ({len(self.issues)}):\\n")
                    for i, issue in enumerate(self.issues, 1):
                        f.write(f"{i}. {issue}\\n")
                    f.write("\\n")
                    
                if self.warnings:
                    f.write(f"⚠️  WARNINGS ({len(self.warnings)}):\\n")
                    for i, warning in enumerate(self.warnings, 1):
                        f.write(f"{i}. {warning}\\n")
                        
        print(f"Report saved to: {output_file}")

if __name__ == "__main__":
    checker = PlatformGuidelinesChecker("/Users/yurielyoung/Book-files-")
    success = checker.check_all_platforms()
    checker.save_report("platform_guidelines.txt")
    
    if success:
        print("\\n🎉 EPUB MEETS ALL PLATFORM REQUIREMENTS")
    else:
        print(f"\\n⚠️  PLATFORM COMPLIANCE ISSUES FOUND")
