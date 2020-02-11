# bibliography

We keep .bib files with the scientific output of the group in this area. The file lab_publications.bib is directly linked to the website and will automatically show your work on the website. This means we need to standardize your entries:

For each bibliography entry, in addition to author, title and year, make sure to include:
* A key: The key will be the first three letter of the last name of the lead author plus a two digit code for the year. So ap aper publiched by Frank Wood in 1920 will be coded as "WOO-20". If more than one publication was publiched by the same person, in the same year, add letters. For example, if our hypothetical Frank Wood had another paper in 1920, it will be coded as "WOO-20a".
* Links (if available): There are four classes of link fields:
** url_Link={}: Use this for a link to the website of the work (for example arxiv).
** url_Paper={}: This will be a direct link to the PDF version of the paper. We recommend linking directly to the PDF on Arxiv.
** url_Presentation={}: This will be a direct link to the PDF version of your presentation for talks you gave at a conference. If your presentation has any animations, make sure to make them static before uploading the PDF. 
** url_Poster={}: This will be a link to the PDF versio nof the poster you prepared. 
* For Arxiv papers, make sure to use archiveprefix = {arXiv}, and eprint = {1906.05462}.
* For presenations and posters (in the presentation or poster bib file), make sure to include event data: eventtitle = {Forschungswelten 2018}, eventdate  = {2018-04-19/2018-04-20}, venue = {St. Gallen, Switzerland}. Or enter them as InProceedings.
* If there is something to point out (say your presentation won an award, etc), make sure to incclude a note using bibbase_note={}.

For the time being, you can upload your presentations and posters to the relevant folders on the Github repository. Over time, these will be reuploaded to the PLAI website. To keep things simple:
* Use the same key as the entry key on the Bibtex file.
* Add _presentation for Presentations
* Add _poster for posters 
