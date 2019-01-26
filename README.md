# Visualization of citation networks
## Tools for bibliometric data collection
### Collecting data from Google Scholar
Google Scholar accounts are arguably the best way to obtain a list of publications of an author. Everybody have Google Scholar profiles and take care to keep it correct and updated. Nevertheless, getting useful publication lists from Google is not straightforward. Below we discuss several ways to get citation data for network visualization.

#### Publish or Perish
It is possible to get citations from Google Scholar using  [Publish or Perish](https://harzing.com/resources/publish-or-perish). PoP is a windows based application, but it can be used on Mac and Linux with the help of Wine. In theory PoP allows literature searches in several databases, however, I was not able to connect to WOS using campus VPN. PoP could be useful to scrape citation results from Google Scholar. Unfortunately, Google truncates author lists unpredictably. In some cases, it retains 5 authors, in other only 3,  and adds '...' at the end of authors. This "..." record appears as a node in the network. Another issue with a shortened list of authors is that the head of a group may very often be the last one, and then the citation will be not connected to the main node. These issues make networks extracted from PoP imported lists not particularly trustworthy. If you decide to go this way, save query results in BibTex format for subsequent network extraction.

#### bibnet-google-scholar-scraper
[Bibnet-google-scholar-scraper](https://github.com/jimmytidey/bibnet-google-scholar-scraper)  allows to search Google Scholar and then collect citations for each item in the search result.  This tool can extract co-author or citation networks and export them in graphviz .dot format. Search results are limited to 10 items per search though. Bibnet-google-scholar-scraper requires javascript developers framework to run it. I have not used this tool myself yet.

#### get_scholar
 [Get_scholar](https://github.com/ssvassiliev/PublicationNetworks)  searches Google Scholar authors by name and then retrieves full records of all publications. This protocol allows circumventing author truncation issue mentioned above. Get_scholar produces a usable list of publications at the expense of query time. Publication records are retrieved one by one, and each query takes a couple of seconds to process, so be patient. The result of a query is saved in BibTex format.<br>
**Installation** 
To install required libraries run the following command:<br>
 `pip install scholarly bibtexparser progress`<br>
**Usage** 
Run the script and follow instructions on the screen. You will be asked to enter the name of the Google Scholar author. The results of the query are saved in BibTex format.

### Collecting data from Pubmed
#### get_citing_authors
[Get_citing_authors](https://github.com/Sihao/get_citing_authors) in an app to get the list of authors citing a given list of papers through the PubMed API. You can either input papers as a comma-separated list of PubMed IDs or provide a search term, and the app will get the authors that cite all of the search results. The output is a table where the first column is author names, the second is the number of times that an author has cited any of the input articles, and the third is the list of PubMed IDs of the cited. The live example can be found [here](https://flask-fetch-citation.herokuapp.com).

### Collecting data from Scopus

## BibTex database clean up

Common issues:
1. Records missing authors, for example, patents!
2. Records missing the principal author
3. The principal author is present, but not recognized because his name in the record is in order (last, middle, first) instead of expected (first, middle, last).
4. Duplicate authors

### cleanup_bibtex.py

## Network extraction
### Sci2 Tool

[Sci2](https://sci2.cns.iu.edu/user/index.php) tool can extract several types of networks from various data formats. It supports major bibliometric formats including ISI, Bibtex Endnote Export Format and Scopus csv. Plain text CSV format is also supported. This introductory workshop will focus on the extraction of networks from BibTex and Scopus files. For more details see [Sci2 manual](http://sci2.wiki.cns.iu.edu) 

Extracting networks from BibTex files.
1. **File** ---> **Load**
2. **Data preparation** ---> **Extract Co-Author Network**. Select bibtex format in popup window.
3. **File **---> **Save**. Select GraphML format in popup window

Troubleshooting problems loading BibTeX files. Sci2 BibTeX parser is picky. You will likely encounter error looking similar to <br>
`"Error parsing BibTeX file: 248:64: encountered '@."`<br>
 What this means is that 64th character on line 248 of this BibTex file is '@'. This character has a special meaning in BibTex, but it also commonly occurs in citation URLs. After removing this character, or escaping it with \@ the file should load normally. 

## Network visualization and analysis

### Gephi

### Graphviz



