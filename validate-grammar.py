#!/usr/bin/env python3
"""
Grammar validation script for Book-files project
Validates grammar in XHTML files using LanguageTool and textstat
"""

import os
import sys
import re
from pathlib import Path
from xml.etree import ElementTree as ET
import argparse
from datetime import datetime

try:
    import language_tool_python
    import textstat
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Error: Required Python packages not installed: {e}")
    print("Please install with: pip3 install language-tool-python textstat beautifulsoup4")
    sys.exit(1)

class GrammarValidator:
    def __init__(self, output_file="grammar-report.txt"):
        self.output_file = output_file
        self.tool = None
        self.error_count = 0
        self.processed_files = 0
        
        # Initialize LanguageTool
        try:
            print("Initializing LanguageTool (this may take a moment)...")
            self.tool = language_tool_python.LanguageTool('en-US')
        except Exception as e:
            print(f"Warning: Could not initialize LanguageTool: {e}")
            print("Grammar checking will be limited.")
    
    def extract_text_from_xhtml(self, file_path):
        """Extract readable text from XHTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse with BeautifulSoup to handle HTML entities properly
            soup = BeautifulSoup(content, 'xml')
            
            # Remove script and style elements
            for element in soup(['script', 'style']):
                element.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            return text
            
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
            return ""
    
    def analyze_readability(self, text):
        """Analyze text readability using textstat"""
        if not text:
            return {}
            
        try:
            stats = {
                'flesch_reading_ease': textstat.flesch_reading_ease(text),
                'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
                'automated_readability_index': textstat.automated_readability_index(text),
                'coleman_liau_index': textstat.coleman_liau_index(text),
                'gunning_fog': textstat.gunning_fog(text),
                'smog_index': textstat.smog_index(text),
                'reading_time': textstat.reading_time(text)
            }
            return stats
        except Exception as e:
            print(f"Error analyzing readability: {e}")
            return {}
    
    def check_grammar(self, text):
        """Check grammar using LanguageTool"""
        if not self.tool or not text:
            return []
            
        try:
            # Split text into chunks to avoid API limits
            chunks = [text[i:i+5000] for i in range(0, len(text), 5000)]
            all_matches = []
            
            for chunk in chunks:
                matches = self.tool.check(chunk)
                all_matches.extend(matches)
            
            return all_matches
        except Exception as e:
            print(f"Error checking grammar: {e}")
            return []
    
    def validate_file(self, file_path):
        """Validate a single XHTML file"""
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
        
        if not file_path.endswith('.xhtml'):
            print(f"Skipping non-XHTML file: {file_path}")
            return True
        
        print(f"Validating grammar in: {os.path.basename(file_path)}")
        
        # Extract text
        text = self.extract_text_from_xhtml(file_path)
        if not text:
            print(f"  Warning: No text extracted from {file_path}")
            return True
        
        # Write to report file
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(f"\n\nFile: {file_path}\n")
            f.write("="*60 + "\n")
            
            # Readability analysis
            f.write("\nREADABILITY ANALYSIS:\n")
            f.write("-"*25 + "\n")
            
            stats = self.analyze_readability(text)
            if stats:
                f.write(f"Flesch Reading Ease: {stats.get('flesch_reading_ease', 'N/A'):.1f}\n")
                f.write(f"Flesch-Kincaid Grade Level: {stats.get('flesch_kincaid_grade', 'N/A'):.1f}\n")
                f.write(f"Automated Readability Index: {stats.get('automated_readability_index', 'N/A'):.1f}\n")
                f.write(f"Coleman-Liau Index: {stats.get('coleman_liau_index', 'N/A'):.1f}\n")
                f.write(f"Gunning Fog Index: {stats.get('gunning_fog', 'N/A'):.1f}\n")
                f.write(f"SMOG Index: {stats.get('smog_index', 'N/A'):.1f}\n")
                f.write(f"Estimated Reading Time: {stats.get('reading_time', 'N/A')} minutes\n")
                
                # Provide readability interpretation
                flesch_score = stats.get('flesch_reading_ease', 0)
                if flesch_score >= 90:
                    f.write("Reading Level: Very Easy (5th grade)\n")
                elif flesch_score >= 80:
                    f.write("Reading Level: Easy (6th grade)\n")
                elif flesch_score >= 70:
                    f.write("Reading Level: Fairly Easy (7th grade)\n")
                elif flesch_score >= 60:
                    f.write("Reading Level: Standard (8th-9th grade)\n")
                elif flesch_score >= 50:
                    f.write("Reading Level: Fairly Difficult (10th-12th grade)\n")
                elif flesch_score >= 30:
                    f.write("Reading Level: Difficult (college level)\n")
                else:
                    f.write("Reading Level: Very Difficult (graduate level)\n")
            
            # Grammar check
            f.write("\nGRAMMAR CHECK RESULTS:\n")
            f.write("-"*25 + "\n")
            
            grammar_issues = self.check_grammar(text)
            
            if grammar_issues:
                f.write(f"Found {len(grammar_issues)} potential grammar issues:\n\n")
                
                for i, match in enumerate(grammar_issues[:20], 1):  # Limit to 20 issues
                    f.write(f"{i}. Issue: {match.message}\n")
                    f.write(f"   Context: '{match.context}'\n")
                    f.write(f"   Suggestion: {', '.join(match.replacements[:3]) if match.replacements else 'No suggestions'}\n")
                    f.write(f"   Category: {match.category}\n")
                    f.write(f"   Rule ID: {match.ruleId}\n\n")
                
                if len(grammar_issues) > 20:
                    f.write(f"... and {len(grammar_issues) - 20} more issues (truncated for readability)\n")
                
                self.error_count += len(grammar_issues)
                print(f"  ✗ Found {len(grammar_issues)} potential grammar issues")
            else:
                f.write("No grammar issues detected.\n")
                print(f"  ✓ No grammar issues found")
        
        self.processed_files += 1
        return True
    
    def run_validation(self, files):
        """Run validation on multiple files"""
        # Initialize report file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("GRAMMAR AND READABILITY VALIDATION REPORT\n")
            f.write("="*60 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"LanguageTool Status: {'Available' if self.tool else 'Not Available'}\n")
            f.write("="*60 + "\n")
        
        # Validate each file
        success = True
        for file_path in files:
            if not self.validate_file(file_path):
                success = False
        
        # Write summary
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write("\n\n" + "="*60 + "\n")
            f.write("SUMMARY\n")
            f.write("="*60 + "\n")
            f.write(f"Files processed: {self.processed_files}\n")
            f.write(f"Total grammar issues: {self.error_count}\n")
            f.write("="*60 + "\n")
        
        print(f"\nGrammar validation completed!")
        print(f"Files processed: {self.processed_files}")
        print(f"Total grammar issues: {self.error_count}")
        print(f"Report saved to: {self.output_file}")
        
        return success and self.error_count == 0

def main():
    parser = argparse.ArgumentParser(description='Grammar validation for EPUB XHTML files')
    parser.add_argument('files', nargs='*', help='XHTML files to validate')
    parser.add_argument('--all', action='store_true', help='Validate all XHTML files in current directory')
    parser.add_argument('--output', default='grammar-report.txt', help='Output report file')
    
    args = parser.parse_args()
    
    # Determine files to process
    if args.all:
        files = list(Path('.').glob('*.xhtml'))
        files = [str(f) for f in files]
    elif args.files:
        files = args.files
    else:
        print("Usage: validate-grammar.py <file1> [file2 ...] or --all")
        print("Example: validate-grammar.py *.xhtml")
        sys.exit(1)
    
    if not files:
        print("No XHTML files found to process.")
        sys.exit(1)
    
    # Run validation
    validator = GrammarValidator(args.output)
    success = validator.run_validation(files)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()