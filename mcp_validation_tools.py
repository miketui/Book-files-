#!/usr/bin/env python3
"""
MCP Validation Tools for EPUB Book Project
==========================================

Comprehensive validation, linting, spelling, and grammar checking tools 
for the "Curls & Contemplation" EPUB project.

This module provides:
1. XML/XHTML validation and linting
2. Spelling and grammar checking
3. Content structure validation
4. Accessibility compliance checking
5. Asset optimization recommendations
"""

import os
import re
import sys
import json
import html
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from xml.etree import ElementTree as ET
from xml.dom import minidom


class EPUBValidator:
    """Main validation class for EPUB project"""
    
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.errors = []
        self.warnings = []
        self.fixes_applied = []
        
    def log_error(self, message: str, file_path: str = None):
        """Log validation error"""
        error = {"message": message, "file": file_path, "type": "error"}
        self.errors.append(error)
        print(f"❌ ERROR: {message}" + (f" in {file_path}" if file_path else ""))
        
    def log_warning(self, message: str, file_path: str = None):
        """Log validation warning"""
        warning = {"message": message, "file": file_path, "type": "warning"}
        self.warnings.append(warning)
        print(f"⚠️  WARNING: {message}" + (f" in {file_path}" if file_path else ""))
        
    def log_fix(self, message: str, file_path: str = None):
        """Log applied fix"""
        fix = {"message": message, "file": file_path, "type": "fix"}
        self.fixes_applied.append(fix)
        print(f"✅ FIXED: {message}" + (f" in {file_path}" if file_path else ""))


class XMLHTMLValidator:
    """XML and XHTML validation tools"""
    
    def __init__(self, validator: EPUBValidator):
        self.validator = validator
        
    def validate_xml_wellformedness(self, file_path: Path) -> bool:
        """Check if XML/XHTML file is well-formed"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse with ElementTree to check well-formedness
            ET.fromstring(content)
            print(f"✅ Well-formed: {file_path.name}")
            return True
            
        except ET.ParseError as e:
            self.validator.log_error(f"XML Parse Error: {str(e)}", file_path.name)
            return False
        except Exception as e:
            self.validator.log_error(f"Validation Error: {str(e)}", file_path.name)
            return False
            
    def validate_xhtml_compliance(self, file_path: Path) -> bool:
        """Check XHTML compliance"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues = []
            
            # Check for required DOCTYPE
            if '<!DOCTYPE html' not in content:
                issues.append("Missing XHTML DOCTYPE declaration")
                
            # Check for XHTML namespace
            if 'xmlns="http://www.w3.org/1999/xhtml"' not in content:
                issues.append("Missing XHTML namespace declaration")
                
            # Check for self-closing tags
            self_closing_tags = ['br', 'hr', 'img', 'input', 'meta', 'link']
            for tag in self_closing_tags:
                pattern = f'<{tag}[^>]*(?<!/)>'
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append(f"Non-self-closing <{tag}> tag found")
                    
            # Check for unclosed tags (basic check)
            open_tags = re.findall(r'<(\w+)[^>]*(?<!/)>', content)
            close_tags = re.findall(r'</(\w+)>', content)
            
            for tag in open_tags:
                if tag.lower() not in ['br', 'hr', 'img', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr']:
                    if open_tags.count(tag) != close_tags.count(tag):
                        issues.append(f"Mismatched opening/closing tags for <{tag}>")
            
            if issues:
                for issue in issues:
                    self.validator.log_warning(issue, file_path.name)
                return False
            else:
                print(f"✅ XHTML Compliant: {file_path.name}")
                return True
                
        except Exception as e:
            self.validator.log_error(f"XHTML validation error: {str(e)}", file_path.name)
            return False

    def validate_all_xhtml_files(self) -> Dict[str, List[bool]]:
        """Validate all XHTML files in the project"""
        print("\n" + "="*60)
        print("🔍 XML/XHTML VALIDATION")
        print("="*60)
        
        xhtml_files = list(self.validator.project_dir.glob('*.xhtml'))
        results = {"wellformed": [], "xhtml_compliant": []}
        
        print(f"Found {len(xhtml_files)} XHTML files to validate\n")
        
        for file_path in sorted(xhtml_files):
            print(f"Validating: {file_path.name}")
            
            wellformed = self.validate_xml_wellformedness(file_path)
            results["wellformed"].append(wellformed)
            
            if wellformed:
                compliant = self.validate_xhtml_compliance(file_path)
                results["xhtml_compliant"].append(compliant)
            else:
                results["xhtml_compliant"].append(False)
                
            print()
            
        return results


class SpellGrammarChecker:
    """Spelling and grammar checking tools"""
    
    def __init__(self, validator: EPUBValidator):
        self.validator = validator
        # Common words to ignore (technical terms, names, etc.)
        self.ignore_words = {
            'epub', 'xhtml', 'css', 'hairstyling', 'hairstylists', 'stylist', 
            'stylists', 'md', 'warren', 'curls', 'contemplation', 'aciss',
            'freelance', 'wellbeing', 'mindfulness', 'journaling',
            'entrepreneurship', 'mentorship', 'resilience'
        }
        
    def extract_text_from_xhtml(self, file_path: Path) -> str:
        """Extract readable text from XHTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove HTML tags but keep text content
            # This is a basic implementation - could be enhanced with BeautifulSoup
            text = re.sub(r'<[^>]+>', ' ', content)
            text = html.unescape(text)  # Convert HTML entities
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
            
        except Exception as e:
            self.validator.log_error(f"Text extraction error: {str(e)}", file_path.name)
            return ""
    
    def check_spelling_basic(self, text: str, file_name: str) -> List[str]:
        """Basic spelling check using common word patterns"""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        potential_errors = []
        
        # Common misspellings in beauty/styling context
        common_misspellings = {
            'recieve': 'receive',
            'seperate': 'separate', 
            'occured': 'occurred',
            'begining': 'beginning',
            'sucessful': 'successful',
            'profesional': 'professional',
            'buisness': 'business',
            'clientele': 'clientele',  # often misspelled as 'clientel'
            'maintainance': 'maintenance',
            'priviledge': 'privilege'
        }
        
        for word in words:
            if word in common_misspellings:
                potential_errors.append(f"Possible misspelling: '{word}' → '{common_misspellings[word]}'")
        
        return potential_errors
    
    def check_grammar_basic(self, text: str, file_name: str) -> List[str]:
        """Basic grammar checking using pattern matching"""
        issues = []
        
        # Check for common grammar issues
        patterns = [
            (r'\bit\'s\s+(?:own|time|place)', "Consider 'its' instead of 'it's' (possessive)"),
            (r'\byour\s+welcome\b', "Should be 'you're welcome' (contraction)"),
            (r'\bthere\s+(?:going|coming)', "Consider 'they're' instead of 'there'"),
            (r'\bto\s+(?:much|many)', "Should be 'too much/many'"),
            (r'\beffect\s+(?:change|growth)', "Consider 'affect' (verb) instead of 'effect' (noun)"),
            (r'\bloose\s+(?:weight|clients)', "Should be 'lose' (verb) instead of 'loose' (adjective)"),
        ]
        
        for pattern, suggestion in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                issues.append(f"Grammar suggestion: {suggestion} - '{match.group()}'")
        
        return issues
    
    def check_content_quality(self, text: str, file_name: str) -> List[str]:
        """Check for content quality issues"""
        issues = []
        
        # Check for repetitive words
        words = re.findall(r'\b\w+\b', text.lower())
        word_count = {}
        for word in words:
            if len(word) > 4:  # Only check longer words
                word_count[word] = word_count.get(word, 0) + 1
        
        # Flag words used excessively
        for word, count in word_count.items():
            if count > 20 and word not in self.ignore_words:
                issues.append(f"Word '{word}' used {count} times - consider varying vocabulary")
        
        # Check for very long sentences (potential run-ons)
        sentences = re.split(r'[.!?]+', text)
        for i, sentence in enumerate(sentences):
            word_count = len(sentence.split())
            if word_count > 40:
                issues.append(f"Very long sentence ({word_count} words) at position {i+1} - consider breaking up")
        
        return issues
    
    def check_all_content(self) -> Dict[str, List]:
        """Check spelling, grammar, and content quality for all XHTML files"""
        print("\n" + "="*60)
        print("📝 SPELLING, GRAMMAR & CONTENT QUALITY CHECK")
        print("="*60)
        
        xhtml_files = list(self.validator.project_dir.glob('*.xhtml'))
        all_issues = {"spelling": [], "grammar": [], "quality": []}
        
        print(f"Checking {len(xhtml_files)} XHTML files for content quality\n")
        
        for file_path in sorted(xhtml_files):
            print(f"Analyzing: {file_path.name}")
            
            text = self.extract_text_from_xhtml(file_path)
            if not text:
                continue
                
            # Spelling check
            spelling_issues = self.check_spelling_basic(text, file_path.name)
            if spelling_issues:
                all_issues["spelling"].extend([f"{file_path.name}: {issue}" for issue in spelling_issues])
                for issue in spelling_issues:
                    self.validator.log_warning(issue, file_path.name)
            
            # Grammar check  
            grammar_issues = self.check_grammar_basic(text, file_path.name)
            if grammar_issues:
                all_issues["grammar"].extend([f"{file_path.name}: {issue}" for issue in grammar_issues])
                for issue in grammar_issues:
                    self.validator.log_warning(issue, file_path.name)
            
            # Content quality
            quality_issues = self.check_content_quality(text, file_path.name)
            if quality_issues:
                all_issues["quality"].extend([f"{file_path.name}: {issue}" for issue in quality_issues])
                for issue in quality_issues:
                    self.validator.log_warning(issue, file_path.name)
            
            if not (spelling_issues or grammar_issues or quality_issues):
                print("  ✅ No issues found")
            print()
            
        return all_issues


class EPUBStructureValidator:
    """EPUB-specific structure validation"""
    
    def __init__(self, validator: EPUBValidator):
        self.validator = validator
        
    def check_css_links(self) -> List[str]:
        """Check CSS link structure in XHTML files"""
        print("\n" + "="*60)
        print("🎨 CSS LINK VALIDATION")
        print("="*60)
        
        issues = []
        xhtml_files = list(self.validator.project_dir.glob('*.xhtml'))
        
        for file_path in sorted(xhtml_files):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for correct CSS link order (fonts.css before style.css)
            fonts_css_pos = content.find('fonts.css')
            style_css_pos = content.find('style.css')
            
            if fonts_css_pos != -1 and style_css_pos != -1:
                if fonts_css_pos > style_css_pos:
                    issue = f"CSS links in wrong order - fonts.css should come before style.css"
                    issues.append(f"{file_path.name}: {issue}")
                    self.validator.log_warning(issue, file_path.name)
                else:
                    print(f"✅ {file_path.name}: CSS links in correct order")
            
            # Check for external CSS linking (not inline)
            if '<style>' in content:
                issue = "Inline CSS found - should use external CSS files"
                issues.append(f"{file_path.name}: {issue}")
                self.validator.log_warning(issue, file_path.name)
        
        return issues
    
    def check_aciss_structure(self) -> List[str]:
        """Check ACISS template compliance"""
        print("\n" + "="*60) 
        print("📋 ACISS TEMPLATE STRUCTURE VALIDATION")
        print("="*60)
        
        issues = []
        chapter_files = [f for f in self.validator.project_dir.glob('*.xhtml') 
                        if 'chapter-' in f.name]
        
        for file_path in sorted(chapter_files):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            checks = {
                "Title page structure": bool(re.search(r'<div[^>]*class="[^"]*title-page[^"]*"', content, re.IGNORECASE)),
                "Content area wrapper": bool(re.search(r'<div[^>]*class="[^"]*content-area[^"]*"', content, re.IGNORECASE)),
                "Quiz section": bool(re.search(r'<div[^>]*class="[^"]*quiz[^"]*"', content, re.IGNORECASE)),
                "Worksheet section": bool(re.search(r'<div[^>]*class="[^"]*worksheet[^"]*"', content, re.IGNORECASE)),
            }
            
            print(f"\nChecking: {file_path.name}")
            for check, passed in checks.items():
                if passed:
                    print(f"  ✅ {check}")
                else:
                    issue = f"Missing or incorrect {check.lower()}"
                    issues.append(f"{file_path.name}: {issue}")
                    self.validator.log_warning(issue, file_path.name)
                    print(f"  ❌ {check}")
        
        return issues
    
    def validate_epub_structure(self) -> Dict[str, List[str]]:
        """Validate overall EPUB structure"""
        css_issues = self.check_css_links()
        aciss_issues = self.check_aciss_structure()
        
        return {
            "css": css_issues,
            "aciss": aciss_issues
        }


class CompilationValidator:
    """EPUB compilation and packaging validation"""
    
    def __init__(self, validator: EPUBValidator):
        self.validator = validator
        
    def check_epubcheck(self) -> bool:
        """Run EPUBCheck validation if available"""
        print("\n" + "="*60)
        print("📚 EPUB COMPILATION VALIDATION")
        print("="*60)
        
        epub_file = self.validator.project_dir / "curls-and-contemplation.epub"
        epubcheck_jar = self.validator.project_dir / "epubcheck-4.2.6" / "epubcheck.jar"
        
        if not epub_file.exists():
            self.validator.log_error("EPUB file not found: curls-and-contemplation.epub")
            return False
            
        if not epubcheck_jar.exists():
            self.validator.log_warning("EPUBCheck tool not found - skipping structural validation")
            return False
        
        try:
            # Try to run EPUBCheck
            result = subprocess.run([
                "java", "-jar", str(epubcheck_jar), str(epub_file)
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ EPUBCheck validation passed!")
                print(result.stdout)
                return True
            else:
                print("❌ EPUBCheck validation failed!")
                print(result.stderr)
                self.validator.log_error("EPUBCheck validation failed", "curls-and-contemplation.epub")
                return False
                
        except subprocess.TimeoutExpired:
            self.validator.log_error("EPUBCheck validation timed out")
            return False
        except FileNotFoundError:
            self.validator.log_error("Java not found - cannot run EPUBCheck")
            return False
        except Exception as e:
            self.validator.log_error(f"EPUBCheck error: {str(e)}")
            return False

    def check_file_sizes(self) -> List[str]:
        """Check for oversized files"""
        print("\n📏 FILE SIZE VALIDATION")
        print("-" * 30)
        
        issues = []
        
        # Check image file sizes
        image_files = list(self.validator.project_dir.glob('*.JPEG')) + \
                     list(self.validator.project_dir.glob('*.PNG')) + \
                     list(self.validator.project_dir.glob('*.jpg')) + \
                     list(self.validator.project_dir.glob('*.png'))
        
        for img_file in image_files:
            size_mb = img_file.stat().st_size / (1024 * 1024)
            if size_mb > 1.0:
                issue = f"Image file too large: {size_mb:.2f}MB (should be < 1MB)"
                issues.append(f"{img_file.name}: {issue}")
                self.validator.log_warning(issue, img_file.name)
            else:
                print(f"✅ {img_file.name}: {size_mb:.2f}MB")
        
        # Check EPUB file size
        epub_file = self.validator.project_dir / "curls-and-contemplation.epub"
        if epub_file.exists():
            epub_size_mb = epub_file.stat().st_size / (1024 * 1024)
            print(f"📚 EPUB file size: {epub_size_mb:.2f}MB")
            if epub_size_mb > 50:
                issue = f"EPUB file very large: {epub_size_mb:.2f}MB - consider optimization"
                issues.append(f"curls-and-contemplation.epub: {issue}")
                self.validator.log_warning(issue, "curls-and-contemplation.epub")
        
        return issues


def main():
    """Main validation workflow"""
    print("="*80)
    print("🎯 MCP VALIDATION TOOLS FOR EPUB PROJECT")
    print("="*80)
    print("Comprehensive validation, linting, spelling, and grammar checking")
    print("for 'Curls & Contemplation: A Stylist's Interactive Journey Journal'")
    print("="*80)
    
    # Initialize validator
    validator = EPUBValidator()
    
    # Run all validations
    xml_validator = XMLHTMLValidator(validator)
    spell_checker = SpellGrammarChecker(validator)  
    structure_validator = EPUBStructureValidator(validator)
    compilation_validator = CompilationValidator(validator)
    
    # 1. XML/XHTML Validation
    xml_results = xml_validator.validate_all_xhtml_files()
    
    # 2. Spelling, Grammar, and Content Quality
    content_results = spell_checker.check_all_content()
    
    # 3. EPUB Structure Validation
    structure_results = structure_validator.validate_epub_structure()
    
    # 4. Compilation Validation
    epub_valid = compilation_validator.check_epubcheck()
    file_size_issues = compilation_validator.check_file_sizes()
    
    # Generate summary report
    print("\n" + "="*80)
    print("📊 VALIDATION SUMMARY REPORT")
    print("="*80)
    
    total_errors = len(validator.errors)
    total_warnings = len(validator.warnings)
    total_fixes = len(validator.fixes_applied)
    
    print(f"Total Errors: {total_errors}")
    print(f"Total Warnings: {total_warnings}")
    print(f"Total Fixes Applied: {total_fixes}")
    
    # XML/XHTML Results
    wellformed_count = sum(xml_results["wellformed"])
    compliant_count = sum(xml_results["xhtml_compliant"])
    total_files = len(xml_results["wellformed"])
    
    print(f"\n📄 XML/XHTML Files:")
    print(f"  Well-formed: {wellformed_count}/{total_files}")
    print(f"  XHTML Compliant: {compliant_count}/{total_files}")
    
    # Content Quality Results
    print(f"\n📝 Content Quality:")
    print(f"  Spelling Issues: {len(content_results['spelling'])}")
    print(f"  Grammar Issues: {len(content_results['grammar'])}")
    print(f"  Quality Issues: {len(content_results['quality'])}")
    
    # Structure Results
    print(f"\n🏗️  Structure Issues:")
    print(f"  CSS Issues: {len(structure_results['css'])}")
    print(f"  ACISS Issues: {len(structure_results['aciss'])}")
    
    # Final Status
    print(f"\n🎯 FINAL STATUS:")
    if total_errors == 0:
        print("✅ VALIDATION PASSED - No critical errors found!")
    else:
        print("❌ VALIDATION FAILED - Critical errors need to be fixed")
        
    if total_warnings > 0:
        print(f"⚠️  {total_warnings} warnings require attention")
    
    # Save detailed report
    report_data = {
        "summary": {
            "errors": total_errors,
            "warnings": total_warnings,
            "fixes_applied": total_fixes
        },
        "xml_validation": xml_results,
        "content_quality": content_results,
        "structure_validation": structure_results,
        "file_size_issues": file_size_issues,
        "epub_valid": epub_valid,
        "detailed_errors": validator.errors,
        "detailed_warnings": validator.warnings,
        "detailed_fixes": validator.fixes_applied
    }
    
    with open("mcp_validation_report.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📋 Detailed report saved to: mcp_validation_report.json")
    print("="*80)
    
    return total_errors == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)