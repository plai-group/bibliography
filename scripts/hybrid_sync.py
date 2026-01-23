#!/usr/bin/env python3

import requests
import re
import sys
import os
import time

INPUT_FILE = "add_publications.txt"
EXISTING_BIB = "group_publications.bib"
OUTPUT_FILE = "group_publications.bib"

# ===== PARSE BIB FILE WITH BRACE COUNTING =====
def parse_bib_entries(content):
    """Parse BibTeX entries by counting braces"""
    entries = []
    entry_pattern = r'@(\w+)\{([^,]+),'
    
    pos = 0
    while True:
        match = re.search(entry_pattern, content[pos:])
        if not match:
            break
        
        start = pos + match.start()
        entry_type = match.group(1)
        citation_key = match.group(2).strip()
        
        brace_count = 1
        i = pos + match.end()
        
        while i < len(content) and brace_count > 0:
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
            i += 1
        
        if brace_count == 0:
            end = i
            full_text = content[start:end]
            
            entry = {
                'ENTRYTYPE': entry_type,
                'ID': citation_key,
                '_full_text': full_text,
                '_start': start,
                '_end': end
            }
            
            doi_match = re.search(r'doi\s*=\s*\{([^}]+)\}', full_text, re.IGNORECASE)
            if doi_match:
                entry['doi'] = doi_match.group(1).strip()
            
            arxiv_match = re.search(r'arxiv\s*=\s*\{([^}]+)\}', full_text, re.IGNORECASE)
            if not arxiv_match:
                arxiv_match = re.search(r'eprint\s*=\s*\{([^}]+)\}', full_text, re.IGNORECASE)
            if arxiv_match:
                entry['arxiv'] = arxiv_match.group(1).strip()
            
            entries.append(entry)
            pos = end
        else:
            pos += match.end()
    
    return entries

# ===== IDENTIFY INPUT TYPE =====
def identify_input(input_str):
    input_str = input_str.strip()
    
    if input_str.startswith('http://') or input_str.startswith('https://'):
        if 'arxiv.org' in input_str:
            match = re.search(r'arxiv\.org/(?:abs|pdf)/(\d{4}\.\d+)', input_str)
            if match:
                return 'arxiv', match.group(1)
        elif 'doi.org' in input_str:
            match = re.search(r'doi\.org/(.+)$', input_str)
            if match:
                return 'doi', match.group(1)
        return 'unknown', input_str
    
    if input_str.startswith('arXiv:'):
        return 'arxiv', input_str.replace('arXiv:', '').strip()
    
    if re.match(r'^\d{4}\.\d{4,5}(v\d+)?$', input_str):
        return 'arxiv', input_str
    
    if input_str.startswith('10.'):
        return 'doi', input_str
    
    return 'unknown', input_str

# ===== LOAD INPUT LIST =====
def load_inputs():
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: {INPUT_FILE} not found")
        sys.exit(1)
    
    with open(INPUT_FILE, 'r') as f:
        inputs = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not inputs:
        print("No inputs to process")
        sys.exit(0)
    
    return inputs

# ===== FETCH FROM CROSSREF =====
def fetch_from_crossref(doi):
    url = f"https://api.crossref.org/works/{doi}"
    headers = {'User-Agent': 'PLAI-Bibliography/1.0 (mailto:plai.execassist@gmail.com)'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
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
        
        pdf_url = ''
        links = work.get('link', [])
        for link in links:
            if link.get('content-type') == 'application/pdf':
                pdf_url = link.get('URL', '')
                break
        
        return {
            'identifier': doi,
            'identifier_type': 'doi',
            'title': title,
            'author': author_str,
            'year': year,
            'venue': container,
            'venue_field': venue_field,
            'entry_type': entry_type,
            'url': url_link,
            'pdf_url': pdf_url,
            'abstract': abstract
        }
    
    except Exception as e:
        print(f"    Error: {e}")
        return None

# ===== FETCH FROM ARXIV =====
def fetch_from_arxiv(arxiv_id):
    arxiv_id = arxiv_id.replace('v', '').strip()
    
    print(f"    Fetching from arXiv API: {arxiv_id}")
    
    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"    HTTP error: {response.status_code}")
            return None
        
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)
        
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entry = root.find('atom:entry', ns)
        
        if entry is None:
            print(f"    No entry found in arXiv response")
            return None
        
        title = entry.find('atom:title', ns)
        title = title.text.strip().replace('\n', ' ') if title is not None else ''
        
        authors = []
        for author in entry.findall('atom:author', ns):
            name = author.find('atom:name', ns)
            if name is not None:
                authors.append(name.text.strip())
        author_str = ' and '.join(authors)
        
        published = entry.find('atom:published', ns)
        year = ''
        if published is not None:
            year = published.text[:4]
        
        abstract_elem = entry.find('atom:summary', ns)
        abstract = abstract_elem.text.strip().replace('\n', ' ') if abstract_elem is not None else ''
        
        url_link = f"https://arxiv.org/abs/{arxiv_id}"
        pdf_link = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        
        return {
            'identifier': arxiv_id,
            'identifier_type': 'arxiv',
            'title': title,
            'author': author_str,
            'year': year,
            'venue': '',
            'venue_field': 'note',
            'entry_type': 'unpublished',
            'url': url_link,
            'pdf_url': pdf_link,
            'abstract': abstract
        }
    
    except Exception as e:
        print(f"    Error: {e}")
        return None

# ===== CREATE BIBTEX TEXT =====
def create_bibtex_text(metadata):
    authors = metadata['author'].split(' and ')
    if authors and authors[0]:
        surname = authors[0].strip().split()[-1].lower()
    else:
        surname = 'unknown'
    
    title = metadata['title']
    stop_words = {'a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or'}
    title_words = [w.lower() for w in title.split() if w.lower() not in stop_words and w.isalnum()]
    title_key = '-'.join(title_words[:3]) if title_words else 'paper'
    
    if len(title_key) > 40:
        title_key = title_key[:40]
    
    citation_key = f"{surname}-{title_key}-{metadata['year']}"
    
    entry_lines = [f"@{metadata['entry_type']}{{{citation_key},"]
    entry_lines.append(f"\ttitle = {{{metadata['title']}}},")
    entry_lines.append(f"\tauthor = {{{metadata['author']}}},")
    entry_lines.append(f"\tyear = {{{metadata['year']}}},")
    
    if metadata['identifier_type'] == 'doi':
        entry_lines.append(f"\tdoi = {{{metadata['identifier']}}},")
    elif metadata['identifier_type'] == 'arxiv':
        entry_lines.append(f"\tarxiv = {{{metadata['identifier']}}},")
    
    if metadata['venue']:
        entry_lines.append(f"\t{metadata['venue_field']} = {{{metadata['venue']}}},")
    
    if metadata['url']:
        entry_lines.append(f"\turl = {{{metadata['url']}}},")
    
    if metadata['pdf_url']:
        entry_lines.append(f"\turl_pdf = {{{metadata['pdf_url']}}},")
    
    if metadata['abstract']:
        abstract_clean = metadata['abstract'].replace('{', '\\{').replace('}', '\\}')
        entry_lines.append(f"\tabstract = {{{abstract_clean}}},")
    
    entry_lines.append("}")
    
    return '\n'.join(entry_lines)

# ===== MAIN =====
def main():
    print("\n" + "="*70)
    print("Publication Sync (DOI / arXiv / URL)")
    print("="*70 + "\n")
    
    inputs = load_inputs()
    print(f"Found {len(inputs)} input(s) to process\n")
    
    if os.path.exists(EXISTING_BIB):
        with open(EXISTING_BIB, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        existing_entries = parse_bib_entries(existing_content)
        print(f"Loaded {len(existing_entries)} existing entries\n")
    else:
        existing_content = ""
        existing_entries = []
    
    identifier_map = {}
    for i, entry in enumerate(existing_entries):
        if 'doi' in entry:
            doi = entry['doi'].lower()
            identifier_map[('doi', doi)] = i
            
            arxiv_match = re.search(r'10\.48550/arxiv\.(\d{4}\.\d+)', doi, re.IGNORECASE)
            if arxiv_match:
                arxiv_id = arxiv_match.group(1)
                identifier_map[('arxiv', arxiv_id.lower())] = i
        
        if 'arxiv' in entry:
            arxiv_id = entry['arxiv'].lower()
            identifier_map[('arxiv', arxiv_id)] = i
    
    new_entries = []
    updated_indices = set()
    failed = 0
    
    for input_str in inputs:
        input_type, identifier = identify_input(input_str)
        
        print(f"Processing: {input_str}")
        print(f"  Detected as: {input_type}")
        
        metadata = None
        
        if input_type == 'doi':
            metadata = fetch_from_crossref(identifier)
        elif input_type == 'arxiv':
            metadata = fetch_from_arxiv(identifier)
        else:
            print(f"  WARNING: Unrecognized format")
            failed += 1
            continue
        
        if metadata:
            key = (metadata['identifier_type'], metadata['identifier'].lower())
            
            if key in identifier_map:
                idx = identifier_map[key]
                updated_indices.add(idx)
                print(f"  UPDATED: {metadata['title'][:60]}")
            else:
                print(f"  ADDED: {metadata['title'][:60]}")
            
            new_entry_text = create_bibtex_text(metadata)
            new_entries.append((key, new_entry_text))
            
            time.sleep(1)
        else:
            failed += 1
    
    if not new_entries:
        print("\nNo valid entries fetched")
        sys.exit(0)
    
    output_parts = []
    
    # Keep entries from 2018 or later, exclude updated ones
    for i, entry in enumerate(existing_entries):
        if i not in updated_indices:
            # Extract year from entry
            year_match = re.search(r'year\s*=\s*\{?(\d{4})\}?', entry['_full_text'], re.IGNORECASE)
            year = int(year_match.group(1)) if year_match else 0
            
            # Only include 2018 and later
            if year >= 2018:
                # Extract title for secondary sort
                title_match = re.search(r'title\s*=\s*\{([^}]+)\}', entry['_full_text'], re.IGNORECASE)
                title = title_match.group(1).lower() if title_match else ''
                
                output_parts.append((year, title, entry['_full_text']))
    
    # Add new entries with their years
    for _, entry_text in new_entries:
        year_match = re.search(r'year\s*=\s*\{(\d{4})\}', entry_text)
        year = int(year_match.group(1)) if year_match else 9999
        
        # Only include 2018 and later
        if year >= 2018:
            title_match = re.search(r'title\s*=\s*\{([^}]+)\}', entry_text, re.IGNORECASE)
            title = title_match.group(1).lower() if title_match else ''
            
            output_parts.append((year, title, entry_text))
    
    # Sort by year descending (newest first), then by title
    output_parts.sort(key=lambda x: (-x[0], x[1]))
    
    # Extract just the text
    sorted_texts = [text for _, _, text in output_parts]
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(sorted_texts))
    
    with open(INPUT_FILE, 'w') as f:
        f.write("# Add new publications here\n")
        f.write("# Insert their DOI, arXiv ID, or URL below (one publication per line)\n")
    
    added = len(new_entries) - len(updated_indices)
    updated = len(updated_indices)
    
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"  Added: {added}")
    print(f"  Updated: {updated}")
    print(f"  Failed: {failed}")
    print(f"  Total entries: {len(existing_entries) - len(updated_indices) + len(new_entries)}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
