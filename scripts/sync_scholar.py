#!/usr/bin/env python3
"""
Process manually exported BibTeX from Google Scholar
Validates, formats, and prepares for website display
"""

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
import sys
import os

INPUT_FILE = "scholar_export.bib"
OUTPUT_FILE = "group_publications.bib"

def clean_entry(entry):
    """Clean and standardize a BibTeX entry"""
    
    # Ensure required fields exist
    if 'title' not in entry or not entry['title']:
        print(f"Warning: Skipping entry without title: {entry.get('ID', 'unknown')}")
        return None
    
    # Standardize author format (Scholar exports with 'and', we keep it)
    if 'author' in entry:
        entry['author'] = entry['author'].strip()
    
    # Ensure year exists
    if 'year' not in entry or not entry['year']:
        entry['year'] = 'unknown'
    
    return entry

def categorize_entries(entries):
    """Organize entries by type for summary"""
    categories = {}
    for entry in entries:
        entry_type = entry.get('ENTRYTYPE', 'misc')
        if entry_type not in categories:
            categories[entry_type] = 0
        categories[entry_type] += 1
    return categories

def main():
    print("="*60)
    print("Google Scholar BibTeX Processor")
    print("="*60)
    
    # Check if input file exists
    if not os.path.exists(INPUT_FILE):
        print(f"\n❌ ERROR: {INPUT_FILE} not found!")
        print("\nTo create this file:")
        print("1. Go to Frank Wood's Scholar profile:")
        print("   https://scholar.google.ca/citations?user=d4yNzXIAAAAJ&hl=en")
        print("2. Check the 'Select all' box at the top")
        print("3. Click 'Export' button")
        print("4. Select 'BibTeX'")
        print("5. Save the downloaded file as 'scholar_export.bib'")
        print("6. Place it in the repository root")
        print("7. Commit and push to GitHub")
        print("8. Run this workflow again")
        sys.exit(1)
    
    print(f"\n✓ Found {INPUT_FILE}")
    
    # Parse the Scholar export
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            parser = bibtexparser.bparser.BibTexParser()
            parser.common_strings = True
            bib_db = parser.parse_file(f)
        
        print(f"✓ Loaded {len(bib_db.entries)} entries from Scholar export")
        
    except Exception as e:
        print(f"\n❌ ERROR parsing {INPUT_FILE}: {e}")
        sys.exit(1)
    
    # Clean and validate entries
    print("\nCleaning and validating entries...")
    cleaned_entries = []
    skipped = 0
    
    for entry in bib_db.entries:
        cleaned = clean_entry(entry)
        if cleaned:
            cleaned_entries.append(cleaned)
        else:
            skipped += 1
    
    if skipped > 0:
        print(f"⚠ Skipped {skipped} incomplete entries")
    
    print(f"✓ {len(cleaned_entries)} valid entries")
    
    # Sort by year (descending) then title
    cleaned_entries.sort(key=lambda x: (-int(x.get('year', 0)) if x.get('year', '').isdigit() else 0, x.get('title', '')))
    
    # Create new database with cleaned entries
    output_db = BibDatabase()
    output_db.entries = cleaned_entries
    
    # Write to output file
    writer = BibTexWriter()
    writer.indent = '\t'
    writer.order_entries_by = None
    
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(writer.write(output_db))
        
        print(f"\n✓ Successfully wrote {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"\n❌ ERROR writing {OUTPUT_FILE}: {e}")
        sys.exit(1)
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    categories = categorize_entries(cleaned_entries)
    for entry_type, count in sorted(categories.items()):
        print(f"  {entry_type}: {count}")
    
    print(f"\nTotal publications: {len(cleaned_entries)}")
    print("\n✓ Processing complete!")
    print("="*60)

if __name__ == "__main__":
    main()
