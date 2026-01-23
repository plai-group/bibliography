# Group Bibliography

This repo helps track papers from our group!

## Publications 
### Semi-automated workflow:
1. Edit add_publications.txt; adding your publication's identifier (DOI, arXiv ID, or URL)
2. Watch as your identifier triggers hybrid-sync.yml to run hybrid_sync.py, which will:
     * Fetch metadata from Crossref API or arXiv API
     * Read group_publications.bib to check for duplicates
     * Updates or adds entries
     * Sorts group_publications.bib by year & title
     * Clears add_publications.txt
3. Our [website](https://plai.cs.ubc.ca/publications/) calls to the group_publications.bib file and displays your work

### Troubleshooting
Publication not added:

* Check the Actions tab for error messages
* Verify the DOI/arXiv ID is correct
* Make sure the identifier is on its own line in add_publications.txt

Missing information:

The automation can only fetch what's available from Crossref/arXiv
Add missing fields manually to group_publications.bib

## Presentations and Posters
Whenever willing, you can upload your presentations and posters folders on this repository 

To keep things simple, the file name should include:
* Abbreviated name of the conference and year
* First author last name (or first three letters of it)
* The type of presentation 
  * Add _presentation for Presentations
  * Add _poster for posters 
