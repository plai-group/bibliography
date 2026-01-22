#!/usr/bin/env python3
"""
Production script to sync Google Scholar publications to group_publications.bib
Maintains existing format and structure with proper venue and type detection
"""

from scholarly import scholarly
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
import sys
import re

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

def determine_entry_type(pub):
    """Determine BibTeX entry type based on venue and other metadata"""
    venue = pub.get('venue', '').lower()
    pub_type = pub.get('pub_type', '').lower()
    
    # Conference indicators
    conference_keywords = [
        'conference', 'proceedings', 'workshop', 'symposium', 
        'icml', 'nips', 'neurips', 'iclr', 'cvpr', 'iccv', 'eccv',
        'aaai', 'ijcai', 'acl', 'emnlp', 'naacl', 'interspeech',
        'icassp', 'sigir', 'kdd', 'www', 'chi', 'uist'
    ]
    
    # Journal indicators
    journal_keywords = [
        'journal', 'transactions', 'letters', 'jmlr', 'pami', 
        'tpami', 'tnnls', 'ieee', 'acm', 'nature', 'science'
    ]
    
    # Preprint indicators  
    preprint_keywords = ['arxiv', 'preprint', 'biorxiv', 'medrxiv']
    
    # Check venue for keywords
    if any(keyword in venue for keyword in conference_keywords):
        return 'inproceedings'
    elif any(keyword in venue for keyword in journal_keywords):
        return 'article'
    elif any(keyword in venue for keyword in preprint_keywords):
        return 'unpublished'
    
    # Check pub_type
    if 'conference' in pub_type or 'inproceedings' in pub_type:
        return 'inproceedings'
    elif 'journal' in pub_type or 'article' in pub_type:
        return 'article'
    elif 'book' in pub_type:
        return 'book'
    
    # Default to misc if can't determine
    return 'misc'

def create_citation_key(pub):
    """Create a unique citation key"""
    # Get first author's last name
    authors = pub.get('author', 'unknown')
    first_author = authors.split(',')[0].split(' and ')[0].strip()
    # Take last word as surname
    surname = first_author.split()[-1].lower() if first_author else 'unknown'
    
    # Get year
    year = pub.get('pub_year', 'nodate')
    
    # Get title words (first 2-3 meaningful words)
    title = pub.get('title', '')
    # Remove common words
    stop_words = {'a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or'}
    title_words = [w.lower() for w in title.split() if w.lower() not in stop_words and w.isalnum()]
    title_key = '-'.join(title_words[:3]) if title_words else 'untitled'
    
    # Limit length
    if len(title_key) > 40:
        title_key = title_key[:40]
    
    return f"{surname}-{title_key}-{year}"

def format_authors(author_string):
    """Format authors from Scholar format to BibTeX format"""
    # Scholar gives: "Author One, Author Two, Author Three"
    # BibTeX wants: "Author One and Author Two and Author Three"
    
    if not author_string:
        return ""
    
    # Split by comma and rejoin with 'and'
    authors = [a.strip() for a in author_string.split(',')]
    return ' and '.join(authors)

def create_bibtex_entry(pub):
    """Convert Scholar publication to BibTeX entry matching existing format"""
    
    entry_type = determine_entry_type(pub)
    citation_key = create_citation_key(pub)
    
    # Build base entry
    entry = {
        'ENTRYTYPE': entry_type,
        'ID': citation_key,
        'title': pub.get('title', ''),
        'author': format_authors(pub.get('author', '')),
        'year': str(pub.get('pub_year', '')),
    }
    
    # Add venue based on entry type
    venue = pub.get('venue', '')
    if venue:
        if entry_type == 'inproceedings':
            entry['booktitle'] = venue
        elif entry_type == 'article':
            entry['journal'] = venue
        elif entry_type == 'book':
            entry['publisher'] = venue
        else:
            # For misc, unpublished, etc., use note field
            entry['note'] = venue
    
    # Add URL if available
    if 'pub_url' in pub and pub['pub_url']:
        entry['url_Paper'] = pub['pub_url']
    
    # Add abstract if available
    if 'abstract' in pub and pub['abstract']:
        entry['abstract'] = pub['abstract']
    
    # Remove empty fields
    return {k: v for k, v in entry.items() if v}

def write_bibtex_file(publications):
    """Write publications to BibTeX file"""
    db = BibDatabase()
    db.entries = []
    
    for pub in publications:
        entry = create_bibtex_entry(pub)
        db.entries.append(entry)
    
    # Sort by year (descending) then title
    db.entries.sort(key=lambda x: (-int(x.get('year', 0)), x.get('title', '')))
    
    writer = BibTexWriter()
    writer.indent = '\t'
    writer.order_entries_by = None
    
    bibtex_str = writer.write(db)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(bibtex_str)
    
    # Print summary by type
    type_counts = {}
    for entry in db.entries:
        entry_type = entry.get('ENTRYTYPE', 'unknown')
        type_counts[entry_type] = type_counts.get(entry_type, 0) + 1
    
    print(f"\nSuccessfully wrote {len(db.entries)} entries to {OUTPUT_FILE}")
    print("\nBreakdown by type:")
    for entry_type, count in sorted(type_counts.items()):
        print(f"  {entry_type}: {count}")

def main():
    publications = fetch_scholar_publications()
    write_bibtex_file(publications)
    print("\nSync complete!")

if __name__ == "__main__":
    main()
