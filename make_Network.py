#!/usr/bin/python
import bibtexparser
import networkx as nx
import numpy
import matplotlib.pyplot as plt


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
nx.draw_networkx_labels(G, pos, labels, alpha=1.0,
                        font_size=8, font_color='black')
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
