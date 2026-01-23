# Group Bibliography

This repo helps track papers from our group!

## Publications

### Semi-automated workflow
Start by:

1. Adding your publication’s identifier (DOI, arXiv ID, or URL — one per line) to [`add_publications.txt`](add_publications.txt).
   
Sit back and watch as:

2. Your commit triggers  [`.github/workflows/add-publications.yml`](.github/workflows/add-publications.yml) to run [`hybrid_sync.py`](https://github.com/plai-group/bibliography/blob/master/scripts/hybrid_sync.py), which will:

   - Fetch metadata from the Crossref or arXiv  
   - Read [`group_publications.bib`](group_publications.bib) to check for duplicates  
   - Update or add entries  
   - Sort [`group_publications.bib`](group_publications.bib) by year & title  
   - Clear [`add_publications.txt`](add_publications.txt)

3. Our [website](https://plai.cs.ubc.ca/publications/) pulls from [`group_publications.bib`](group_publications.bib) to display your work.

### Troubleshooting

**Publication not added?**

- Check the **Actions** tab for error messages  
- Make sure each identifier is correct and on its own line in [`add_publications.txt`](add_publications.txt)

**Missing information?**

- The automation can only fetch what’s available from Crossref or arXiv.  
- Add missing fields manually to [`group_publications.bib`](group_publications.bib).


## Presentations and Posters

When possible, upload your presentation and poster folders to this repository.

To keep things simple, file names should include:

- Abbreviated conference name and year  
- First author’s last name (or first three letters)  
- Type of presentation  
  - Add `_presentation` for presentations  
  - Add `_poster` for posters
