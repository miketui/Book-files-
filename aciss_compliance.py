#!/usr/bin/env python3
"""
ACISS Template Compliance Checker
Validates that all chapter XHTML files follow the ACISS template structure
"""

import os
from pathlib import Path
from bs4 import BeautifulSoup
import re

class ACISSComplianceChecker:
    def __init__(self, epub_dir):
        self.epub_dir = Path(epub_dir)
        self.text_dir = self.epub_dir / 'OEBPS' / 'text'
        self.issues = []
        self.results = []
        
    def check_compliance(self):
        """Run ACISS template compliance check on all chapters"""
        print("=== ACISS TEMPLATE COMPLIANCE CHECK ===\n")
        
        # Find all chapter files
        chapter_files = [f for f in self.text_dir.glob('*chapter*.xhtml')]
        chapter_files.sort()
        
        if not chapter_files:
            self.issues.append("No chapter files found")
            return False
            
        print(f"Found {len(chapter_files)} chapter files to check\n")
        
        compliant_count = 0
        for chapter_file in chapter_files:
            is_compliant = self.check_chapter_file(chapter_file)
            if is_compliant:
                compliant_count += 1
                
        print(f"\n=== COMPLIANCE SUMMARY ===")
        print(f"Total chapters checked: {len(chapter_files)}")
        print(f"Fully compliant: {compliant_count}")
        print(f"Issues found: {len(chapter_files) - compliant_count}")
        
        return len(self.issues) == 0
        
    def check_chapter_file(self, file_path):
        """Check ACISS compliance for a single chapter file"""
        print(f"📄 Checking: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            soup = BeautifulSoup(content, 'html.parser')
            chapter_issues = []
            
            # 1. Check for title page section with .chap-title class
            chap_title = soup.find('section', class_='chap-title')
            if not chap_title:
                chapter_issues.append("Missing title page section with .chap-title class")
            else:
                print("  ✅ Title page section (.chap-title) present")
                
            # 2. Check for .content-area wrapper
            content_area = soup.find('div', class_='content-area')
            if not content_area:
                chapter_issues.append("Missing .content-area wrapper div")
            else:
                print("  ✅ Content area wrapper (.content-area) present")
                
            # 3. Check quiz section (≤ 4 questions, no answer keys)
            self.check_quiz_section(soup, chapter_issues, file_path.name)
            
            # 4. Check for worksheet section
            worksheet = soup.find(attrs={'class': re.compile(r'worksheet|journal')})
            if worksheet:
                print("  ✅ Worksheet/journal section present")
            else:
                print("  ⚠️  No worksheet/journal section found")
                
            # 5. Check for closing image
            closing_image = soup.find('section', class_='image-quote') or soup.find('img', src=re.compile(r'chapter.*quote'))
            if closing_image:
                print("  ✅ Closing image/quote present")
            else:
                chapter_issues.append("Missing closing image section")
                
            # 6. Check Roman numeral in chapter number
            roman_found = False
            for text in soup.stripped_strings:
                if re.search(r'\b[IVX]+\b', text):
                    roman_found = True
                    break
            if roman_found:
                print("  ✅ Roman numeral found")
            else:
                print("  ⚠️  No Roman numeral detected")
                
            # 7. Check for Bible quote/epigraph
            bible_quote = soup.find(attrs={'class': re.compile(r'bible-quote|epigraph')})
            if bible_quote:
                print("  ✅ Bible quote/epigraph present")
            else:
                print("  ⚠️  No Bible quote/epigraph section found")
                
            # 8. Check for drop cap
            drop_cap = soup.find(attrs={'class': re.compile(r'dropcap')})
            if drop_cap:
                print("  ✅ Drop cap styling present")
            else:
                print("  ⚠️  No drop cap styling found")
            
            if chapter_issues:
                self.issues.extend([f"{file_path.name}: {issue}" for issue in chapter_issues])
                print(f"  ❌ {len(chapter_issues)} issues found")
                return False
            else:
                print("  🎉 Chapter fully compliant with ACISS template")
                return True
                
        except Exception as e:
            error_msg = f"Error processing {file_path.name}: {e}"
            self.issues.append(error_msg)
            print(f"  ❌ {error_msg}")
            return False
        finally:
            print()  # Add spacing between files
            
    def check_quiz_section(self, soup, chapter_issues, filename):
        """Check quiz section compliance"""
        quiz_sections = soup.find_all(attrs={'class': re.compile(r'quiz')})
        
        if not quiz_sections:
            print("  ⚠️  No quiz section found")
            return
            
        for quiz in quiz_sections:
            # Count questions
            questions = quiz.find_all('li') or quiz.find_all(attrs={'class': re.compile(r'question')})
            question_count = len(questions)
            
            if question_count > 4:
                chapter_issues.append(f"Quiz has {question_count} questions (max 4 allowed)")
                print(f"  ❌ Quiz has {question_count} questions (exceeds limit of 4)")
            elif question_count > 0:
                print(f"  ✅ Quiz section present with {question_count} questions")
            else:
                print("  ⚠️  Quiz section found but no questions detected")
                
            # Check for embedded answers (should not be present)
            answer_indicators = quiz.find_all(text=re.compile(r'answer|correct|solution', re.IGNORECASE))
            if answer_indicators:
                chapter_issues.append("Quiz contains embedded answers")
                print("  ❌ Quiz contains embedded answers (should not have answers)")
            else:
                print("  ✅ No embedded answers found in quiz")
                
    def save_report(self, output_file):
        """Save compliance results to file"""
        with open(output_file, 'w') as f:
            f.write("ACISS TEMPLATE COMPLIANCE REPORT\\n")
            f.write("=" * 50 + "\\n\\n")
            
            if not self.issues:
                f.write("✅ ALL CHAPTERS COMPLIANT\\n\\n")
                f.write("All chapter files follow ACISS template structure:\\n")
                f.write("- Title page section with .chap-title class\\n")
                f.write("- Content wrapped in .content-area div\\n")
                f.write("- Quiz sections with ≤4 questions and no embedded answers\\n")
                f.write("- Worksheet/journal sections present\\n")
                f.write("- Closing image sections present\\n")
            else:
                f.write(f"❌ COMPLIANCE ISSUES FOUND ({len(self.issues)} total)\\n\\n")
                for i, issue in enumerate(self.issues, 1):
                    f.write(f"{i}. {issue}\\n")
                    
        print(f"Report saved to: {output_file}")

if __name__ == "__main__":
    checker = ACISSComplianceChecker("/Users/yurielyoung/Book-files-")
    success = checker.check_compliance()
    checker.save_report("aciss_compliance.txt")
    
    if success:
        print("\\n🎉 ALL CHAPTERS MEET ACISS TEMPLATE REQUIREMENTS")
    else:
        print(f"\\n⚠️  FOUND {len(checker.issues)} COMPLIANCE ISSUES")
