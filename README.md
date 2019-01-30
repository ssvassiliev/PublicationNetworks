# Network visualization

## Tools for bibliometric data collection

#### get_scholar
 Get_scholar script searches Google Scholar authors by name and then retrieves full records of all publications. This protocol allows circumventing author truncation issue mentioned above. Get_scholar produces a usable list of publications at the expense of query time. Publication records are retrieved one by one, and each query takes a couple of seconds to process, so be patient. The result of a query is saved in BibTex format.<br>
**Installation**
To install required libraries run the following command:<br>
 `pip install scholarly bibtexparser progress`<br>
**Usage**
Run the script and follow instructions on the screen. You will be asked to enter the name of the Google Scholar author. The result of the query is saved in BibTex format.


## Preprocessing BibTex database

preprocess_authors script removes records missing all authors, records missing only principal author, and attempts to merge duplicate authors. it will not be able to merge all misspelled authors. Suspected duplicates can be saved in the file "name-dupl-out.csv", corrected  interactively, or ignored.  The file has all similar pairs of authors flagged witn 'n' , meaning do not merge. To tell program to merge a pair of authors user changes 'n' to 'y', changes filename to "name-dupl-in.csv" and reruns the program.


## Network extraction

make_co-author_network extracts network from BibTex file and saves it in GraphML format.

### make_citation_network_scopus

make_citation_network_scopus  extracts network from BibTex file exported by Scopus and saves it in GraphML format. 
