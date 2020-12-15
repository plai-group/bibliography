# Group Bibliography

We keep .bib files with the scientific output of the group in this area. You can also upload the final version of your presentations and posters in this repository; they will be slowly transitioned to the PLAI Group website.

You will receive a reminder every few months to update the repositories here.

## Group Publications Bibtex File
The file group_publications.bib is directly linked to the website and will automatically show your work on the website. This means we need to standardize your entries.

For each bibliography entry, in addition to author, title and year, make sure to include:
* The correct entry type. The script used on the website uses the type to distinguish between entries. Common entry types:
  * article: For articles published in journals
  * inproceedings: For conference proceedings
  * unpublished: Work that is not formally published (say recent work that is underreview and you have posted on Arxiv).
* A key: The key will be the first three letter of the last name of the lead author plus a two digit code for the year. So a paper published by Frank Wood in 1920 will be coded as "WOO-20". If more than one publication was published by the same person, in the same year, add letters. For example, if our hypothetical Frank Wood had another paper in 1920, it will be coded as "WOO-20a".
* Links (if available): There are four classes of link fields:
  * url_Link={}: Use this for a link to the website of the work (for example arxiv).
  * url_Paper={}: This will be a direct link to the PDF version of the paper. We recommend linking directly to the PDF on Arxiv.
  * url_Presentation={}: This will be a direct link to the PDF version of your presentation for talks you gave at a conference. If your presentation has any animations, make sure to make them static before uploading the PDF. You can upload your presentation on Github as per the instructions below.
  * url_Poster={}: This will be a link to the PDF versio nof the poster you prepared. You can upload your poster on Github as per the instructions below.
  * url_Arxiv={}: Arxiv link
* doi is strongly recommended if your work has one.
* For Arxiv papers, make sure to use archiveprefix = {arXiv}, and eprint = {1906.05462}.
* For presenations and posters, make sure to include event data: eventtitle = {Forschungswelten 2018}, eventdate  = {2018-04-19/2018-04-20}, venue = {St. Gallen, Switzerland}. Or enter them as InProceedings.
* Make sure to include both the full name of the Journal/Conference and its abbreviated form.
* If there is something to point out (say your presentation won an award, etc), make sure to include a note using bibbase_note={}.
* Make sure to include your funding source name in the keyword field. These currently include: D3M, LwLL, Intel, NSERC.

Please make sure that you add new entries (recent years) at the top. The file is intentionally ordered by year to help check if we have all published items from each year or not.

For sample entries, check [here](https://bibbase.org/show?bib=http://www.cs.toronto.edu/~fritz/publications/list.bib&theme=dividers).

## Presentations and Posters
For the time being, you can upload your presentations and posters to the relevant folders on the Github repository. Over time, these will be reuploaded to the PLAI website. 

We just need the final version of your presentations and posters here, preferably in PDF. To keep things simple:
* Use the same key as the entry key on the Bibtex file.
* The name of the conference
* The type of presentation 
  * Add _presentation for Presentations
  * Add _poster for posters 
An example file nam would look like WOO19_NeurIPS2019_presentation. This is a presentation/talk, done by an author withe last name wood, in 2019 at NeurIPS2019.

Remember Github maximum repository size is 100 GB and maximum file size is 100 MB.
