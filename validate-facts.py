#!/usr/bin/env python3
"""
Fact-checking workflow script for Book-files project
Validates factual claims, citations, and bibliography entries in XHTML files
"""

import os
import sys
import re
import json
from pathlib import Path
from xml.etree import ElementTree as ET
import argparse
from datetime import datetime
from urllib.parse import urlparse

try:
    from bs4 import BeautifulSoup
    import requests
except ImportError as e:
    print(f"Error: Required Python packages not installed: {e}")
    print("Please install with: pip3 install beautifulsoup4 requests")
    sys.exit(1)

class FactChecker:
    def __init__(self, output_file="fact-check-report.txt"):
        self.output_file = output_file
        self.issues_found = 0
        self.processed_files = 0
        self.bibliography_entries = []
        self.citations_found = []
        self.urls_to_check = []
        
        # Patterns for detecting claims that need verification
        self.fact_patterns = [
            r'\b\d{4}\b',  # Years
            r'\b\d+%\b',   # Percentages
            r'\$[\d,]+',   # Dollar amounts
            r'\b(?:study|research|survey|report)\s+(?:shows|found|indicates)\b',  # Research claims
            r'\b(?:according to|research by|study by)\b',  # Attribution patterns
        ]
        
        # Patterns for URLs and citations
        self.url_pattern = r'https?://[^\s<>"]+(?:\.[^\s<>"]+)*'
        self.citation_pattern = r'(?:ibid\.|id\.|cf\.|see|p\.\s*\d+|\d{4})'
        
    def extract_text_from_xhtml(self, file_path):
        """Extract readable text from XHTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'xml')
            
            # Remove script and style elements
            for element in soup(['script', 'style']):
                element.decompose()
            
            return soup.get_text(), soup
            
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
            return "", None
    
    def extract_bibliography_entries(self, soup):
        """Extract bibliography entries from the document"""
        entries = []
        
        # Look for bibliography-specific patterns
        if soup:
            # Find list items that look like bibliography entries
            list_items = soup.find_all(['li', 'p'])
            
            for item in list_items:
                text = item.get_text().strip()
                
                # Check if this looks like a bibliography entry
                if (len(text) > 50 and 
                    (re.search(r'\b(19|20)\d{2}\b', text) or  # Contains year
                     'http' in text or  # Contains URL
                     '.' in text[-10:])):  # Ends with period (common in citations)
                    
                    entries.append({
                        'text': text,
                        'urls': re.findall(self.url_pattern, text),
                        'year': re.findall(r'\b(19|20)\d{2}\b', text),
                    })
        
        return entries
    
    def check_urls(self, urls, max_check=5):
        """Check if URLs are accessible (limited checking)"""
        results = []
        
        for i, url in enumerate(urls[:max_check]):  # Limit to avoid rate limiting
            try:
                # Basic URL validation
                parsed = urlparse(url)
                if not parsed.scheme or not parsed.netloc:
                    results.append({
                        'url': url,
                        'status': 'invalid',
                        'message': 'Invalid URL format'
                    })
                    continue
                
                # Very basic connectivity test (timeout quickly)
                response = requests.head(url, timeout=5, allow_redirects=True)
                
                results.append({
                    'url': url,
                    'status': 'accessible' if response.status_code < 400 else 'error',
                    'status_code': response.status_code,
                    'message': f'HTTP {response.status_code}'
                })
                
            except requests.RequestException as e:
                results.append({
                    'url': url,
                    'status': 'error',
                    'message': str(e)[:100] + '...' if len(str(e)) > 100 else str(e)
                })
            except Exception as e:
                results.append({
                    'url': url,
                    'status': 'error',
                    'message': f'Check failed: {str(e)[:50]}...'
                })
        
        if len(urls) > max_check:
            results.append({
                'url': f'... and {len(urls) - max_check} more URLs',
                'status': 'not_checked',
                'message': 'URL checking limited to prevent rate limiting'
            })
        
        return results
    
    def find_factual_claims(self, text):
        """Find potential factual claims that need verification"""
        claims = []
        
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue
            
            for pattern in self.fact_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    claims.append({
                        'sentence': sentence,
                        'pattern_matched': pattern,
                        'type': self._classify_claim_type(sentence)
                    })
                    break
        
        return claims[:10]  # Limit to prevent overwhelming output
    
    def _classify_claim_type(self, sentence):
        """Classify the type of factual claim"""
        sentence_lower = sentence.lower()
        
        if any(word in sentence_lower for word in ['study', 'research', 'survey']):
            return 'research_claim'
        elif any(word in sentence_lower for word in ['$', 'cost', 'price', 'revenue']):
            return 'financial_claim'
        elif re.search(r'\b\d+%', sentence):
            return 'statistical_claim'
        elif re.search(r'\b\d{4}\b', sentence):
            return 'date_claim'
        else:
            return 'general_claim'
    
    def validate_file(self, file_path):
        """Validate factual content in a single XHTML file"""
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
        
        if not file_path.endswith('.xhtml'):
            print(f"Skipping non-XHTML file: {file_path}")
            return True
        
        print(f"Fact-checking: {os.path.basename(file_path)}")
        
        # Extract text and parse
        text, soup = self.extract_text_from_xhtml(file_path)
        if not text:
            print(f"  Warning: No text extracted from {file_path}")
            return True
        
        # Find bibliography entries (especially important for bibliography.xhtml)
        bib_entries = self.extract_bibliography_entries(soup)
        
        # Find URLs
        urls = re.findall(self.url_pattern, text)
        
        # Find potential factual claims
        claims = self.find_factual_claims(text)
        
        # Check URLs (limited to avoid rate limiting)
        url_results = []
        if urls:
            print(f"  → Checking {min(5, len(urls))} URLs...")
            url_results = self.check_urls(urls)
        
        # Write to report file
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(f"\n\nFile: {file_path}\n")
            f.write("="*60 + "\n")
            
            # Bibliography analysis
            if bib_entries:
                f.write(f"\nBIBLIOGRAPHY ENTRIES FOUND: {len(bib_entries)}\n")
                f.write("-"*30 + "\n")
                
                for i, entry in enumerate(bib_entries[:10], 1):  # Limit output
                    f.write(f"{i}. {entry['text'][:200]}{'...' if len(entry['text']) > 200 else ''}\n")
                    if entry['urls']:
                        f.write(f"   URLs: {', '.join(entry['urls'][:3])}\n")
                    if entry['year']:
                        f.write(f"   Years mentioned: {', '.join(entry['year'][:3])}\n")
                    f.write("\n")
                
                if len(bib_entries) > 10:
                    f.write(f"... and {len(bib_entries) - 10} more entries\n")
            
            # URL validation results
            if url_results:
                f.write(f"\nURL VALIDATION RESULTS: {len([r for r in url_results if 'url' in r])}\n")
                f.write("-"*30 + "\n")
                
                for result in url_results:
                    if 'status_code' in result:
                        f.write(f"✓ {result['url']} - {result['message']}\n")
                    elif result['status'] == 'error':
                        f.write(f"✗ {result['url']} - {result['message']}\n")
                        self.issues_found += 1
                    elif result['status'] == 'invalid':
                        f.write(f"⚠ {result['url']} - {result['message']}\n")
                        self.issues_found += 1
                    else:
                        f.write(f"- {result['url']} - {result['message']}\n")
            
            # Factual claims analysis
            if claims:
                f.write(f"\nFACTUAL CLAIMS IDENTIFIED: {len(claims)}\n")
                f.write("-"*30 + "\n")
                f.write("NOTE: These claims may need manual verification:\n\n")
                
                for i, claim in enumerate(claims, 1):
                    f.write(f"{i}. [{claim['type'].upper()}] {claim['sentence'][:150]}{'...' if len(claim['sentence']) > 150 else ''}\n\n")
            
            # Summary for this file
            file_issues = len([r for r in url_results if r.get('status') == 'error'])
            f.write(f"\nFILE SUMMARY:\n")
            f.write(f"Bibliography entries: {len(bib_entries)}\n")
            f.write(f"URLs found: {len(urls)}\n")
            f.write(f"URLs checked: {len([r for r in url_results if 'status_code' in r or r.get('status') in ['error', 'invalid']])}\n")
            f.write(f"URL issues: {file_issues}\n")
            f.write(f"Factual claims identified: {len(claims)}\n")
        
        # Update counters
        self.processed_files += 1
        
        if bib_entries or urls or claims:
            print(f"  ✓ Found {len(bib_entries)} bibliography entries, {len(urls)} URLs, {len(claims)} factual claims")
        else:
            print(f"  - No bibliography entries, URLs, or notable factual claims found")
        
        return True
    
    def run_validation(self, files):
        """Run fact-checking on multiple files"""
        # Initialize report file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("FACT-CHECKING AND BIBLIOGRAPHY VALIDATION REPORT\n")
            f.write("="*60 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n")
            f.write("\nNOTE: This report identifies potential factual claims and validates\n")
            f.write("bibliography entries. Manual verification is recommended for all\n")
            f.write("factual claims, especially research citations and statistics.\n")
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
            f.write(f"Issues found: {self.issues_found}\n")
            f.write("\nRECOMMENDATIONS:\n")
            f.write("1. Manually verify all research claims and statistics\n")
            f.write("2. Check accessibility of all cited URLs\n")
            f.write("3. Ensure all bibliography entries are properly formatted\n")
            f.write("4. Verify dates and numerical claims for accuracy\n")
            f.write("="*60 + "\n")
        
        print(f"\nFact-checking validation completed!")
        print(f"Files processed: {self.processed_files}")
        print(f"Issues found: {self.issues_found}")
        print(f"Report saved to: {self.output_file}")
        
        return success

def main():
    parser = argparse.ArgumentParser(description='Fact-checking validation for EPUB XHTML files')
    parser.add_argument('files', nargs='*', help='XHTML files to validate')
    parser.add_argument('--all', action='store_true', help='Validate all XHTML files in current directory')
    parser.add_argument('--output', default='fact-check-report.txt', help='Output report file')
    parser.add_argument('--check-urls', action='store_true', help='Enable URL accessibility checking')
    
    args = parser.parse_args()
    
    # Determine files to process
    if args.all:
        files = list(Path('.').glob('*.xhtml'))
        files = [str(f) for f in files]
    elif args.files:
        files = args.files
    else:
        print("Usage: validate-facts.py <file1> [file2 ...] or --all")
        print("Example: validate-facts.py *.xhtml")
        sys.exit(1)
    
    if not files:
        print("No XHTML files found to process.")
        sys.exit(1)
    
    # Run validation
    checker = FactChecker(args.output)
    success = checker.run_validation(files)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()