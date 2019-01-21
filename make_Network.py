#!/usr/bin/python
import bibtexparser
import networkx as nx
import jellyfish

bibtex_file = open('data/Zaraiskaya.bib')
bib_str = bibtex_file.read()
bib_db = bibtexparser.loads(bib_str)

G = nx.Graph
threshold = 0.85

def make_uniq_authors_list(bib_db):
    allAuthors = []
    for entry in bib_db.entries:
        if 'author' not in entry:
            continue
        authors = entry['author'].split(' and ')
        authors = map(unicode.strip, authors)
        for author in authors:
            if author not in allAuthors:
                allAuthors.append(author)
            else:
                continue
    return allAuthors


def make_pairs(allAuthors, threshold):
    pairs = []
    np = 0
    for i in range(0, len(allAuthors)):
        for j in range(i+1, len(allAuthors)):
            djawi_1 = jellyfish.jaro_winkler(allAuthors[i], allAuthors[j])
            djawi_2 = jellyfish.jaro_winkler(allAuthors[i].split()[-1], allAuthors[j].split()[-1])
            if djawi_1 > threshold or djawi_2 > threshold:
                np = np + 1
                while(1):
                    q = allAuthors[i] + ' --> ' + allAuthors[j] + ' (y/i/n)?'
                    choice = raw_input(q.encode('ascii', 'ignore'))
                    if choice == 'y':
                        p = (allAuthors[i], allAuthors[j])
                        pairs.append(p)
                        break
                    elif choice == 'i':
                        p = (allAuthors[j], allAuthors[i])
                        pairs.append(p)
                        break
                    elif choice == 'n':
                        break
                    else:
                        continue
    print '---------------------------------'
    print 'Merging: ' + str(len(pairs)) + ' authors'
    return(np, pairs)


def rename_authors(bib_db, pairs):
    for entry in bib_db.entries:
        if 'author' not in entry:
            continue
        for p in pairs:
            entry['author'] = entry['author'].replace(p[0], p[1])
    return(pairs)


print('')
while(1):
    allAuthors = make_uniq_authors_list(bib_db)
    print 'Total number of authors = ' + str(len(allAuthors)) + '\n'
    choice = raw_input("Merge duplicate authors (y/n)?")
    print('')
    if choice == 'y':
        np, pairs = make_pairs(allAuthors, threshold)
        if np == 0:
            break
        rename_authors(bib_db, pairs)
    elif choice == 'n':
        break
    else:
        continue
