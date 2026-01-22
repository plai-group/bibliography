#!/usr/bin/env python3

import requests
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
import sys
import os
import time

DOI_LIST_FILE = "dois_to_add.txt"
EXISTING_BIB = "group_publications.bib"
OUTPUT_FILE = "group_publications.bib"

# ===== LOAD DOI LIST =====
def load_dois():
    if not os.path.exists(DOI_LIST_FILE):
        print(f"ERROR: {DOI_LIST_FILE} not found")
        sys.exit(1)
    
    with open(DOI_LIST_FILE, 'r') as f:
        dois = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not dois:
        print("No DOIs to process")
        sys.exit(0)
    
    return dois

# ===== FETCH METADATA FROM CROSSREF =====
def fetch_metadata(doi):
    doi = doi.strip().replace('https://doi.org/', '').replace('http://doi.org/', '')
    
    url = f"https://api.crossref.org/works/{doi}"
    headers = {'User-Agent': 'PLAI-Bibliography/1.0 (mailto:plai@cs.ubc.ca)'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 404:
            print(f"  WARNING: DOI not found: {doi}")
            return None
        
        if response.status_code != 200:
            print(f"  WARNING: Error {response.status_code} for DOI: {doi}")
            return None
        
        work = response.json().get('message', {})
        
        title = work.get('title', [''])[0] if work.get('title') else ''
        
        authors = []
        for author in work.get('author', []):
            given = author.get('given', '')
            family = author.get('family', '')
            if family:
                authors.append(f"{given} {family}".strip())
        author_str = ' and '.join(authors)
        
        published = work.get('published-print') or work.get('published-online') or work.get('created')
        year = ''
        if published and 'date-parts' in published:
            year = str(published['date-parts'][0][0])
        
        container = work.get('container-title', [''])[0] if work.get('container-title') else ''
        
        pub_type = work.get('type', '')
        if pub_type == 'journal-article':
            entry_type = 'article'
            venue_field = 'journal'
        elif 'proceedings' in pub_type or 'conference' in container.lower():
            entry_type = 'inproceedings'
            venue_field = 'booktitle'
        else:
            entry_type = 'misc'
            venue_field = 'note'
        
        url_link = work.get('URL', f"https://doi.org/{doi}")
        abstract = work.get('abstract', '')
        
        return {
            'doi': doi,
            'title': title,
            'author': author_str,
            'year': year,
            'venue': container,
            'venue_field': venue_field,
            'entry_type': entry_type,
            'url': url_link,
            'abstract': abstract
        }
    
    except Exception as e:
        print(f"  ERROR fetching {doi}: {e}")
        return None

# ===== CREATE BIBTEX ENTRY =====
def create_bibtex_entry(metadata):
    authors = metadata['author'].split(' and ')
    if authors:
        surname = authors[0].strip().split()[-1].lower() if authors[0] else 'unknown'
    else:
        surname = 'unknown'
    
    title = metadata['title']
    stop_words = {'a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or'}
    title_words = [w.lower() for w in title.split() if w.lower() not in stop_words and w.isalnum()]
    title_key = '-'.join(title_words[:3]) if title_words else 'paper'
    
    if len(title_key) > 40:
        title_key = title_key[:40]
    
    citation_key = f"{surname}-{title_key}-{metadata['year']}"
    
    entry = {
        'ENTRYTYPE': metadata['entry_type'],
        'ID': citation_key,
        'title': metadata['title'],
        'author': metadata['author'],
        'year': metadata['year'],
        'doi': metadata['doi'],
    }
    
    if metadata['venue']:
        entry[metadata['venue_field']] = metadata['venue']
    
    if metadata['url']:
        entry['url'] = metadata['url']
    
    if metadata['abstract']:
        entry['abstract'] = metadata['abstract']
    
    return {k: v for k, v in entry.items() if v}

# ===== LOAD EXISTING BIBLIOGRAPHY =====
def load_existing_bib():
    if not os.path.exists(EXISTING_BIB):
        return BibDatabase()
    
    with open(EXISTING_BIB, 'r', encoding='utf-8') as f:
        parser = bibtexparser.bparser.BibTexParser()
        return parser.parse_file(f)

# ===== MERGE ENTRIES =====
def merge_entries(existing_db, new_entries):
    existing_dois = {}
    for i, entry in enumerate(existing_db.entries):
        if 'doi' in entry:
            existing_dois[entry['doi'].lower()] = i
    
    added = 0
    updated = 0
    
    for new_entry in new_entries:
        doi = new_entry['doi'].lower()
        
        if doi in existing_dois:
            idx = existing_dois[doi]
            existing_db.entries[idx] = new_entry
            updated += 1
            print(f"  UPDATED: {new_entry['title'][:60]}")
        else:
            existing_db.entries.append(new_entry)
            added += 1
            print(f"  ADDED: {new_entry['title'][:60]}")
    
    return added, updated

# ===== WRITE OUTPUT =====
def write_output(db):
    db.entries.sort(
        key=lambda x: (
            -int(x.get('year', 0)) if str(x.get('year', '')).isdigit() else 0,
            x.get('title', '')
        )
    )
    
    writer = BibTexWriter()
    writer.indent = '\t'
    writer.order_entries_by = None
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(writer.write(db))

# ===== CLEAR DOI LIST =====
def clear_doi_list():
    with open(DOI_LIST_FILE, 'w') as f:
        f.write("# Add DOIs here, one per line\n")
        f.write("# Lines starting with # are ignored\n")

# ===== MAIN =====
def main():
    print("\n" + "="*70)
    print("DOI-Based Publication Sync")
    print("="*70 + "\n")
    
    dois = load_dois()
    print(f"Found {len(dois)} DOI(s) to process\n")
    
    existing_db = load_existing_bib()
    print(f"Loaded {len(existing_db.entries)} existing entries\n")
    
    new_entries = []
    failed = 0
    
    for doi in dois:
        print(f"Fetching: {doi}")
        metadata = fetch_metadata(doi)
        
        if metadata:
            entry = create_bibtex_entry(metadata)
            new_entries.append(entry)
            time.sleep(1)
        else:
            failed += 1
    
    if not new_entries:
        print("\nNo valid entries fetched")
        sys.exit(0)
    
    print(f"\n{'='*70}")
    added, updated = merge_entries(existing_db, new_entries)
    
    write_output(existing_db)
    
    clear_doi_list()
    
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"  Added: {added}")
    print(f"  Updated: {updated}")
    print(f"  Failed: {failed}")
    print(f"  Total entries: {len(existing_db.entries)}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
