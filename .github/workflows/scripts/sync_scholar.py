#!/usr/bin/env python3
"""
Production script to sync Google Scholar publications to group_publications.bib
Maintains existing format and structure
"""

from scholarly import scholarly
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
import sys

SCHOLAR_ID = "d4yNzXIAAAAJ"  # Frank Wood
OUTPUT_FILE = "group_publications.bib"

def fetch_scholar_publications():
    """Fetch all publications from Frank Wood's Google Scholar profile"""
    print("Fetching publications from Google Scholar...")
    
    try:
        author = scholarly.search_author_id(SCHOLAR_ID)
        author_filled = scholarly.fill(author)
        
        print(f"Author: {author_filled['name']}")
        print(f"Total publications found: {len(author_filled['publications'])}")
        
        publications = []
        for i, pub in enumerate(author_filled['publications']):
            print(f"Processing {i+1}/{len(author_filled['publications'])}: {pub['bib']['title'][:50]}...")
            
            # Get full publication details
            pub_filled = scholarly.fill(pub)
            publications.append(pub_filled['bib'])
        
        return publications
        
    except Exception as e:
        print(f"Error fetching from Scholar: {e}")
        sys.exit(1)

def create_bibtex_entry(pub, index):
    """Convert Scholar publication to BibTeX entry matching existing format"""
    
    # Determine entry type
    pub_type = pub.get('pub_type', 'misc').lower()
    if 'conference' in pub.get('venue', '').lower():
        entry_type = 'inproceedings'
    elif 'journal' in pub.get('venue', '').lower() or 'article' in pub_type:
        entry_type = 'article'
    elif 'arxiv' in pub.get('venue', '').lower() or 'preprint' in pub_type:
        entry_type = 'unpublished'
    else:
        entry_type = 'misc'
    
    # Create citation key (author-year format)
    first_author = pub.get('author', 'unknown').split(',')[0].split()[-1].lower()
    year = pub.get('pub_year', 'nodate')
    title_words = pub.get('title', '').split()[:3]
    title_key = '-'.join(word.lower() for word in title_words if word.isalnum())
    citation_key = f"{first_author}-{title_key}-{year}"
    
    # Build entry
    entry = {
        'ENTRYTYPE': entry_type,
        'ID': citation_key,
        'title': pub.get('title', ''),
        'author': pub.get('author', '').replace(' and ', ', '),
        'year': str(pub.get('pub_year', '')),
    }
    
    # Add venue-specific fields
    venue = pub.get('venue', '')
    if entry_type == 'inproceedings':
        entry['booktitle'] = venue
    elif entry_type == 'article':
        entry['journal'] = venue
    elif venue:
        entry['note'] = venue
    
    # Add optional fields
    if 'url' in pub:
        entry['url'] = pub['url']
    if 'abstract' in pub:
        entry['abstract'] = pub['abstract']
    
    # Remove empty fields
    return {k: v for k, v in entry.items() if v}

def write_bibtex_file(publications):
    """Write publications to BibTeX file"""
    db = BibDatabase()
    db.entries = []
    
    for i, pub in enumerate(publications):
        entry = create_bibtex_entry(pub, i)
        db.entries.append(entry)
    
    # Sort by year (descending) then title
    db.entries.sort(key=lambda x: (-int(x.get('year', 0)), x.get('title', '')))
    
    writer = BibTexWriter()
    writer.indent = '\t'
    writer.order_entries_by = None  # Keep our custom sort
    
    bibtex_str = writer.write(db)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(bibtex_str)
    
    print(f"\nSuccessfully wrote {len(db.entries)} entries to {OUTPUT_FILE}")

def main():
    publications = fetch_scholar_publications()
    write_bibtex_file(publications)
    print("Sync complete!")

if __name__ == "__main__":
    main()
