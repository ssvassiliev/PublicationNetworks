#!/usr/bin/python
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
import networkx as nx
import jellyfish
import numpy
import matplotlib.pyplot as plt
import os


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
            djawi_2 = jellyfish.jaro_winkler(allAuthors[i].split()[-1],
                                             allAuthors[j].split()[-1])
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


def save_all_pairs(allAuthors, threshold):
    pairs = []
    np = 0
    for i, auth_1 in enumerate(allAuthors):
        for auth_2 in allAuthors[i+1:-1]:
            djawi_1 = jellyfish.jaro_winkler(auth_1, auth_2)
            djawi_2 = jellyfish.jaro_winkler(auth_1.split()[-1],
                                             auth_2.split()[-1])
            if djawi_1 > threshold or djawi_2 > threshold:
                np = np + 1
                p = (auth_1, auth_2)
                pairs.append(p)
    f = open("duplicates.csv", "w+")
    f.write('\n'.join('%s, %s, y' % x for x in pairs).encode('utf-8'))
    f.close()
    return(pairs)


def rename_authors(bib_db, pairs):
    for entry in bib_db.entries:
        if 'author' not in entry:
            continue
        for p in pairs:
            entry['author'] = entry['author'].replace(p[0], p[1])
    return(pairs)


# Main program
infile = raw_input('Enter name of BibTex file:')
out_graphml = infile.replace(".bib", ".graphml")
out_bib = infile.replace(".bib", "-edited.bib")
# Jaro-Winkler threshold
threshold = 0.85
# Graph parameters
maxNodeSize = 200
maxEdgeWidth = 3
G = nx.Graph()
bibtex_file = open(infile)
bib_str = bibtex_file.read()
bib_db = bibtexparser.loads(bib_str)
print('Constructing network from file: ' + infile)
# Make the list of unique authors
allAuthors = make_uniq_authors_list(bib_db)
pairs = save_all_pairs(allAuthors, threshold)
# Graph
msize = len(allAuthors)
edges = numpy.zeros((msize, msize))
weights = numpy.zeros(msize)
for entry in bib_db.entries:
    if 'author' not in entry:
        continue
    authors = entry['author'].split(' and ')
    authors = map(unicode.strip, authors)
    for author in authors:
        il = allAuthors.index(author)
        weights[il] = weights[il] + 1
        for author_2 in authors:
            e2 = allAuthors.index(author_2)
            e1 = allAuthors.index(author)
            if e1 != e2:
                edges[e1][e2] = edges[e1][e2] + 1
# Normalize weights of nodes and edges
wm = weights.max()
for i, each_weight in enumerate(weights):
    weights[i] = each_weight*maxNodeSize/wm
for i in range(0, msize):
    G.add_node(i, weight=weights[i], label=allAuthors[i])
    for j in range(i+1, msize):
        if edges[i][j] != 0:
            G.add_edge(i, j, weight=edges[i][j]*maxEdgeWidth/edges.max())
# Save graph
nx.write_graphml(G, out_graphml)

# Draw graph
labels = dict((n, d['label']) for (n, d) in G.nodes(data=True))
edgewidth = [d['weight'] for (u, v, d) in G.edges(data=True)]
nodesize = [d['weight'] for (u, d) in G.nodes(data=True)]
pos = nx.spring_layout(G, iterations=100)
nx.draw_networkx_nodes(G, pos, node_size=nodesize)
nx.draw_networkx_edges(G, pos, width=0.5, edge_color='b')
nx.draw_networkx_labels(G, pos, labels, alpha=1.0, font_size=8,
                                            font_color='black')
plt.axis('off')
plt.show()

# Draw Hub Ego graph
# from operator import itemgetter
# node_and_degree = G.degree()
# (largest_hub, degree) = sorted(node_and_degree, key=itemgetter(1))[-1]
# Create ego graph of main hub
# hub_ego = nx.ego_graph(G, largest_hub)
# Draw graph
# pos = nx.spring_layout(hub_ego
# nx.draw(hub_ego, pos, node_color='b', node_size=50, with_labels=False)
# Draw ego as large and red
# nx.draw_networkx_nodes(hub_ego, pos, nodelist=[largest_hub], node_size=300, node_color='r')
# plt.show()
