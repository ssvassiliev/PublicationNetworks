#!/usr/bin/python
import scholarly
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
from progress.bar import Bar

scholar = raw_input('Search Google Scholar: ')
outfile = scholar.split()[-1] + '.bib'
db = BibDatabase()
authors = []
count = 0
search_query = scholarly.search_author(scholar)
for au in search_query:
    count = count + 1
    print "\nProfile #" + str(count) + ': ' + au.name
    print 'Affiliation: ' + au.affiliation
    print 'Email: ' + au.email
    line = ''
    for i in au.interests:
        line = line + unicode(i) + ', '
    print 'Interests: ' + line.rstrip(',')
    authors.append(au)
if count > 1:
    s = 'Select profile (1-' + str(count) + "): "
    ind = input(s)
    ind = ind - 1
else:
    ind = 0
print 'Downloading ' + authors[ind].name + ' publications'
author = authors[ind].fill()
db.entries = []
id = 1
bar = Bar('Loading', max=len(author.publications))
for id, p in enumerate(author.publications):
    bar.next()
    pub = p.fill()
    if 'year' in pub.bib:
        pub.bib['year'] = str(pub.bib['year'])
    pub.bib['ENTRYTYPE'] = unicode('article')
    if 'abstract' in pub.bib:
        del pub.bib['abstract']
    sid = "%04d" % id
    pub.bib['ID'] = str(sid)
    db.entries.append(pub.bib)
bar.finish()
writer = BibTexWriter()
bibtex_str = bibtexparser.dumps(db)
with open(outfile, 'w') as bibfile:
    bibfile.write(bibtex_str.encode('utf8'))
