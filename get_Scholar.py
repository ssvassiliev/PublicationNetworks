#!/usr/bin/python
import scholarly
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
from progress.bar import Bar
from multiprocessing.dummy import Pool
import time
import pause
import random

number_publications = 0


def download_publications(p):
    pause.seconds(random.random())
    publ = p.fill()
    return(publ)


# make the Pool of workers
pool = Pool(4)
scholar = raw_input('Search Google Scholar: ')
# scholar = 'bruce balcom'
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
pub = []
id = 1
number_publications = len(author.publications)
bar = Bar('Loading', max=number_publications)
start = time.time()
pb = pool.imap(download_publications, author.publications)
for i in pb:
    bar.next()
bar.finish()
pool.close()
pool.join()
pub = list(pb)
end = time.time()
print "Download time: " + str(end - start)

for id, publ in enumerate(pub):
    if 'year' in publ.bib:
        publ.bib['year'] = str(publ.bib['year'])
    publ.bib['ENTRYTYPE'] = unicode('article')
    if 'abstract' in publ.bib:
        del publ.bib['abstract']
    sid = "%04d" % id
    publ.bib['ID'] = str(sid)
    db.entries.append(publ.bib)

writer = BibTexWriter()
bibtex_str = bibtexparser.dumps(db)
with open(outfile, 'w') as bibfile:
    bibfile.write(bibtex_str.encode('utf8'))
