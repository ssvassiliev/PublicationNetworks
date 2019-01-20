# Bibnet-google-scholar


# Google scholar
It is possible to get citations from Google Scholar using "Publish or Perish":
https://harzing.com/resources/publish-or-perish
PoP is windows program, but it can be used on Mac and Linux with the help of Wine.
It allows to perform literature searches in several databases, however I was not able to use it with WOS with VPN.
It may be useful to scrape citation results from Google Scholar.
Save query results in BibTex format.
Use Sci2 to construct network. Only Co-author network can be extracted, because neither Scholar not PoP provide citations (WOS does if .isi format is used)
Save network in GraphML format.

Note: bibtex format (coming from PoP) adds "..." after first 5 authors, so this "..." appears as a node in the network. This node should be manually deleted from the network. Another issue with shortened list of authors is that the author of interest may quite well be the last one and in this case the citation will be disconnected from the main node.  

Workflow:
1. Use PoP to query Scholar and save BibTex
2. Use sci2 to read BibTex, extract co-author network and save in GraphML format
3. Use gephi to visualize GraphML file
