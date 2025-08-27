#!/usr/bin/env python3
"""
Manifest and Spine Cross-Check Audit
Validates content.opf against actual filesystem and checks for inconsistencies
"""

import os
from pathlib import Path
from lxml import etree
import sys

class ManifestAuditor:
    def __init__(self, epub_dir):
        self.epub_dir = Path(epub_dir)
        self.oebps_dir = self.epub_dir / 'OEBPS'
        self.content_opf = self.oebps_dir / 'content.opf'
        self.issues = []
        
    def audit(self):
        """Run complete manifest and spine audit"""
        print("=== MANIFEST & SPINE AUDIT ===\n")
        
        if not self.content_opf.exists():
            self.issues.append("CRITICAL: content.opf not found")
            return False
            
        # Parse content.opf
        tree = etree.parse(self.content_opf)
        ns = {'opf': 'http://www.idpf.org/2007/opf'}
        
        # Get all manifest items and spine items
        manifest_items = tree.xpath('//opf:item', namespaces=ns)
        spine_items = tree.xpath('//opf:itemref', namespaces=ns)
        
        self.check_manifest_files(manifest_items)
        self.check_orphan_files(manifest_items)
        self.check_spine_integrity(manifest_items, spine_items)
        
        return len(self.issues) == 0
        
    def check_manifest_files(self, manifest_items):
        """Check if all manifest entries correspond to actual files"""
        print("1. MANIFEST FILE EXISTENCE CHECK")
        print("-" * 40)
        
        missing_files = []
        for item in manifest_items:
            href = item.get('href')
            file_path = self.oebps_dir / href
            
            if not file_path.exists():
                missing_files.append(f"Missing: {href} (referenced in manifest)")
                
        if missing_files:
            self.issues.extend(missing_files)
            for missing in missing_files:
                print(f"❌ {missing}")
        else:
            print("✅ All manifest entries have corresponding files")
            
        print(f"Total manifest items: {len(manifest_items)}")
        print(f"Missing files: {len(missing_files)}\n")
        
    def check_orphan_files(self, manifest_items):
        """Check for files in OEBPS not referenced in manifest"""
        print("2. ORPHAN FILES CHECK")
        print("-" * 40)
        
        # Get all manifest hrefs
        manifest_hrefs = {item.get('href') for item in manifest_items}
        
        # Find all files in OEBPS (excluding content.opf)
        orphan_files = []
        for root, dirs, files in os.walk(self.oebps_dir):
            for file in files:
                if file == 'content.opf':
                    continue
                    
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.oebps_dir)
                
                if str(relative_path) not in manifest_hrefs:
                    orphan_files.append(str(relative_path))
                    
        if orphan_files:
            self.issues.append(f"Found {len(orphan_files)} orphan files not in manifest")
            for orphan in orphan_files:
                print(f"⚠️  Orphan: {orphan}")
        else:
            print("✅ No orphan files found")
            
        print(f"Total OEBPS files: {len(manifest_hrefs) + len(orphan_files) + 1}")  # +1 for content.opf
        print(f"Orphan files: {len(orphan_files)}\n")
        
    def check_spine_integrity(self, manifest_items, spine_items):
        """Check spine references and reading order"""
        print("3. SPINE INTEGRITY CHECK")
        print("-" * 40)
        
        # Create manifest ID lookup
        manifest_ids = {item.get('id'): item.get('href') for item in manifest_items}
        
        # Check spine references
        spine_issues = []
        xhtml_count = 0
        
        for i, spine_item in enumerate(spine_items):
            idref = spine_item.get('idref')
            
            if idref not in manifest_ids:
                spine_issues.append(f"Spine item {i+1}: ID '{idref}' not found in manifest")
            else:
                href = manifest_ids[idref]
                if href.endswith('.xhtml'):
                    xhtml_count += 1
                    
        if spine_issues:
            self.issues.extend(spine_issues)
            for issue in spine_issues:
                print(f"❌ {issue}")
        else:
            print("✅ All spine items reference valid manifest entries")
            
        # Check for proper reading order (numbered files should be in order)
        reading_order_issues = []
        prev_num = 0
        
        for spine_item in spine_items:
            idref = spine_item.get('idref')
            if idref in manifest_ids:
                href = manifest_ids[idref]
                if href.startswith('text/') and href[5].isdigit():
                    try:
                        file_num = int(href.split('-')[0][5:])  # Extract number from filename
                        if file_num < prev_num:
                            reading_order_issues.append(f"Reading order issue: {href} (#{file_num}) after #{prev_num}")
                        prev_num = file_num
                    except (ValueError, IndexError):
                        pass  # Skip if parsing fails
                        
        if reading_order_issues:
            self.issues.extend(reading_order_issues)
            for issue in reading_order_issues:
                print(f"⚠️  {issue}")
        else:
            print("✅ Reading order appears correct")
            
        print(f"Total spine items: {len(spine_items)}")
        print(f"XHTML files in spine: {xhtml_count}")
        print(f"Spine issues: {len(spine_issues + reading_order_issues)}\n")
        
    def save_report(self, output_file):
        """Save audit results to file"""
        with open(output_file, 'w') as f:
            f.write("MANIFEST & SPINE AUDIT REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            if not self.issues:
                f.write("✅ AUDIT PASSED - No issues found\n\n")
                f.write("All manifest entries correspond to existing files\n")
                f.write("No orphan files detected\n") 
                f.write("Spine references are valid and in correct order\n")
            else:
                f.write(f"❌ AUDIT FOUND {len(self.issues)} ISSUES\n\n")
                for i, issue in enumerate(self.issues, 1):
                    f.write(f"{i}. {issue}\n")
                    
        print(f"Report saved to: {output_file}")

if __name__ == "__main__":
    auditor = ManifestAuditor("/Users/yurielyoung/Book-files-")
    success = auditor.audit()
    auditor.save_report("opf_audit.txt")
    
    if success:
        print("🎉 MANIFEST & SPINE AUDIT PASSED")
        sys.exit(0)
    else:
        print("⚠️  MANIFEST & SPINE AUDIT FOUND ISSUES")
        sys.exit(1)
