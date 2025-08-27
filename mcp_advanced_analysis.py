#!/usr/bin/env python3
"""
MCP Fact-Checking and Advanced Content Analysis Tools
=====================================================

Advanced fact-checking, content analysis, and quality assurance tools
specifically designed for the "Curls & Contemplation" EPUB project.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import Counter
import urllib.parse


class FactChecker:
    """Fact-checking and content verification tools"""
    
    def __init__(self):
        self.beauty_industry_facts = {
            # Common beauty industry statistics and facts to verify
            "hair_growth_rate": "0.5 inches per month",  # approximately
            "hair_cycle_phases": ["anagen", "catagen", "telogen"],
            "professional_licensing": "varies by state",
            "salon_industry_size": "billions",  # US hair care industry
        }
        
        # Technical terms that should be consistent
        self.technical_terms = {
            "pH": ["ph", "Ph", "PH"],  # Should be "pH"
            "sulfate": ["sulphate"],   # US vs UK spelling
            "color": ["colour"],       # US vs UK spelling
            "keratin": ["keratine"],   # Common misspelling
        }
    
    def check_technical_accuracy(self, text: str, file_name: str) -> List[str]:
        """Check for technical accuracy in beauty/hair content"""
        issues = []
        
        # Check for common technical inaccuracies
        accuracy_checks = [
            (r'\bpH\s*=\s*14', "pH 14 is extremely alkaline - unlikely for hair products"),
            (r'\bpH\s*=\s*0', "pH 0 is extremely acidic - dangerous for hair/skin"),
            (r'\bhair\s+grows?\s+\d+\s+inches?\s+per\s+day', "Hair growth per day is unrealistic - should be per month"),
            (r'\bsulfates?\s+are\s+always\s+bad', "Overgeneralization - sulfates have legitimate uses"),
            (r'\bsilicones?\s+are\s+always\s+bad', "Overgeneralization - silicones can be beneficial"),
            (r'\bnatural\s+means\s+safe', "Naturalistic fallacy - natural doesn't always mean safe"),
        ]
        
        for pattern, concern in accuracy_checks:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"Potential technical inaccuracy: {concern}")
        
        return issues
    
    def check_consistency(self, text: str, file_name: str) -> List[str]:
        """Check for terminology consistency"""
        issues = []
        
        for correct_term, variations in self.technical_terms.items():
            for variation in variations:
                pattern = r'\b' + re.escape(variation) + r'\b'
                if re.search(pattern, text, re.IGNORECASE):
                    issues.append(f"Inconsistent terminology: '{variation}' should be '{correct_term}'")
        
        return issues
    
    def check_claims_and_citations(self, text: str, file_name: str) -> List[str]:
        """Check for unsupported claims that might need citations"""
        issues = []
        
        # Patterns that typically need citation
        claim_patterns = [
            (r'\bstudies? shows?', "Claims about studies should include citations"),
            (r'\bresearch proves?', "Research claims should include citations"),  
            (r'\bscientists? (found|discovered|proved)', "Scientific claims should include citations"),
            (r'\b\d+%\s+of\s+(people|clients|customers)', "Statistical claims should include sources"),
            (r'\baccording to experts?', "Expert opinions should name the experts"),
        ]
        
        for pattern, suggestion in claim_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                issues.append(f"Citation needed: {suggestion} (found {len(matches)} instances)")
        
        return issues


class ContentAnalyzer:
    """Advanced content analysis tools"""
    
    def __init__(self):
        # Beauty and styling specific vocabulary
        self.domain_vocabulary = {
            "hair_types": ["straight", "wavy", "curly", "coily", "fine", "thick", "damaged", "healthy"],
            "techniques": ["blow-dry", "diffusing", "plopping", "scrunching", "protective styling"],
            "products": ["shampoo", "conditioner", "leave-in", "gel", "mousse", "cream", "serum"],
            "tools": ["diffuser", "brush", "comb", "clips", "scissors", "razor"],
            "business_terms": ["freelance", "client", "booking", "consultation", "portfolio", "marketing"],
        }
    
    def analyze_readability(self, text: str) -> Dict[str, float]:
        """Basic readability analysis"""
        sentences = re.split(r'[.!?]+', text)
        words = re.findall(r'\b\w+\b', text)
        
        if len(sentences) == 0 or len(words) == 0:
            return {"avg_sentence_length": 0, "avg_word_length": 0}
        
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        return {
            "avg_sentence_length": avg_sentence_length,
            "avg_word_length": avg_word_length,
            "total_words": len(words),
            "total_sentences": len(sentences)
        }
    
    def analyze_domain_coverage(self, text: str) -> Dict[str, int]:
        """Analyze coverage of domain-specific vocabulary"""
        text_lower = text.lower()
        coverage = {}
        
        for category, terms in self.domain_vocabulary.items():
            found_terms = [term for term in terms if term in text_lower]
            coverage[category] = len(found_terms)
        
        return coverage
    
    def find_accessibility_issues(self, text: str) -> List[str]:
        """Find potential accessibility issues in content"""
        issues = []
        
        # Check for images without alt text descriptions
        if 'image' in text.lower() or 'figure' in text.lower() or 'photo' in text.lower():
            if 'alt=' not in text and 'described as' not in text.lower():
                issues.append("Images may need alt text descriptions for accessibility")
        
        # Check for color-only descriptions
        color_only_patterns = [
            r'\bclick\s+the\s+(red|blue|green|yellow)\s+button',
            r'\bsee\s+the\s+(red|blue|green|yellow)\s+(text|link)',
        ]
        
        for pattern in color_only_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append("Color-only instructions may not be accessible - provide additional cues")
        
        return issues


class LinkChecker:
    """Check for broken or problematic links"""
    
    def __init__(self):
        pass
    
    def extract_links(self, content: str) -> List[str]:
        """Extract all links from content"""
        # Extract href attributes
        href_pattern = r'href=["\']([^"\']+)["\']'
        links = re.findall(href_pattern, content, re.IGNORECASE)
        return links
    
    def categorize_links(self, links: List[str]) -> Dict[str, List[str]]:
        """Categorize links by type"""
        categories = {
            "internal": [],
            "external": [],
            "email": [],
            "anchor": [],
            "relative": []
        }
        
        for link in links:
            if link.startswith('#'):
                categories["anchor"].append(link)
            elif link.startswith('mailto:'):
                categories["email"].append(link)
            elif link.startswith('http://') or link.startswith('https://'):
                categories["external"].append(link)
            elif '/' in link and not link.startswith('#'):
                categories["relative"].append(link)
            else:
                categories["internal"].append(link)
        
        return categories


def main():
    """Run advanced content analysis"""
    print("="*70)
    print("🔍 MCP FACT-CHECKING & ADVANCED CONTENT ANALYSIS")
    print("="*70)
    
    project_dir = Path(".")
    xhtml_files = list(project_dir.glob('*.xhtml'))
    
    fact_checker = FactChecker()
    content_analyzer = ContentAnalyzer()
    link_checker = LinkChecker()
    
    all_results = {
        "fact_checking": [],
        "consistency": [],
        "citations": [],
        "readability": {},
        "domain_coverage": {},
        "accessibility": [],
        "links": {}
    }
    
    print(f"Analyzing {len(xhtml_files)} files for advanced content issues...\n")
    
    for file_path in sorted(xhtml_files):
        print(f"📖 Analyzing: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract text content (basic)
            text = re.sub(r'<[^>]+>', ' ', content)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Fact checking
            fact_issues = fact_checker.check_technical_accuracy(text, file_path.name)
            consistency_issues = fact_checker.check_consistency(text, file_path.name)
            citation_issues = fact_checker.check_claims_and_citations(text, file_path.name)
            
            if fact_issues:
                all_results["fact_checking"].extend([f"{file_path.name}: {issue}" for issue in fact_issues])
                print(f"  ⚠️  {len(fact_issues)} fact-checking concerns")
            
            if consistency_issues:
                all_results["consistency"].extend([f"{file_path.name}: {issue}" for issue in consistency_issues])
                print(f"  ⚠️  {len(consistency_issues)} consistency issues")
                
            if citation_issues:
                all_results["citations"].extend([f"{file_path.name}: {issue}" for issue in citation_issues])
                print(f"  📚 {len(citation_issues)} citation suggestions")
            
            # Content analysis
            readability = content_analyzer.analyze_readability(text)
            all_results["readability"][file_path.name] = readability
            
            domain_coverage = content_analyzer.analyze_domain_coverage(text)
            all_results["domain_coverage"][file_path.name] = domain_coverage
            
            accessibility_issues = content_analyzer.find_accessibility_issues(content)
            if accessibility_issues:
                all_results["accessibility"].extend([f"{file_path.name}: {issue}" for issue in accessibility_issues])
                print(f"  ♿ {len(accessibility_issues)} accessibility concerns")
            
            # Link analysis
            links = link_checker.extract_links(content)
            if links:
                link_categories = link_checker.categorize_links(links)
                all_results["links"][file_path.name] = link_categories
                print(f"  🔗 {len(links)} links found")
            
            if not any([fact_issues, consistency_issues, citation_issues, accessibility_issues]):
                print("  ✅ No issues found")
                
        except Exception as e:
            print(f"  ❌ Error analyzing {file_path.name}: {e}")
        
        print()
    
    # Generate summary report
    print("="*70)
    print("📊 ADVANCED ANALYSIS SUMMARY")
    print("="*70)
    
    print(f"Fact-checking concerns: {len(all_results['fact_checking'])}")
    print(f"Consistency issues: {len(all_results['consistency'])}")
    print(f"Citation suggestions: {len(all_results['citations'])}")
    print(f"Accessibility concerns: {len(all_results['accessibility'])}")
    
    # Readability summary
    all_word_counts = [data["total_words"] for data in all_results["readability"].values()]
    total_words = sum(all_word_counts)
    avg_sentence_lengths = [data["avg_sentence_length"] for data in all_results["readability"].values()]
    
    print(f"\n📖 Readability Overview:")
    print(f"  Total words across all files: {total_words:,}")
    print(f"  Average sentence length: {sum(avg_sentence_lengths)/len(avg_sentence_lengths):.1f} words")
    
    # Domain coverage summary
    domain_totals = {}
    for file_coverage in all_results["domain_coverage"].values():
        for category, count in file_coverage.items():
            domain_totals[category] = domain_totals.get(category, 0) + count
    
    print(f"\n🎯 Domain Vocabulary Usage:")
    for category, total in domain_totals.items():
        print(f"  {category.replace('_', ' ').title()}: {total} terms used")
    
    # Save detailed report
    with open("mcp_advanced_analysis.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📋 Detailed analysis saved to: mcp_advanced_analysis.json")
    print("="*70)


if __name__ == "__main__":
    main()