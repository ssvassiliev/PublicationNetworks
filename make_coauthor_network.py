#!/usr/bin/python
import bibtexparser
import networkx as nx
import numpy
import matplotlib.pyplot as plt
from progress.bar import Bar


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


def extract_ref_authors_scopus(db_entry):
    references = db_entry['references'].split(';')
    authors = []
    for reference in references:
        title_end_index = reference.find('(')
        t_author = reference[0:title_end_index]
        i_authors_end = t_author.rfind('.,')
        author_list = t_author[0:i_authors_end+1].split('.,')
        for i, item in enumerate(author_list):
            author_list[i] = item.replace(',', '').\
             replace('.', '').replace(' der ', ' ').strip()
            la = author_list[i].split()
            le = la[0]
            la[0] = la[-1]
            la[-1] = le
            author_list[i] = ' '.join(la)
        authors.append(author_list)
    return(authors)


if __name__ == "__main__":
    infile = raw_input('Enter name of BibTex file:')
    out_graphml = infile.replace(".bib", ".graphml")
    out_bib = infile.replace(".bib", "-edited.bib")
    # Graph parameters
    maxNodeSize = 200
    maxEdgeWidth = 3
    bibtex_file = open(infile)
    bib_str = bibtex_file.read()
    bib_db = bibtexparser.loads(bib_str)
    print('Constructing network from file: ' + infile)
    # Make the list of unique authors
    allAuthors = make_uniq_authors_list(bib_db)
    # Create network
    G = nx.Graph()
    msize = len(allAuthors)
    edges = numpy.zeros((msize, msize))
    weights = numpy.zeros(msize)
    # Fill co-author matrix
    bar = Bar('Processing BibTex', max=len(bib_db.entries))
    for entry in bib_db.entries:
        bar.next()
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
    bar.finish()
    # Add normalized nodes and edges
    wm = weights.max()
    for i, each_weight in enumerate(weights):
        weights[i] = each_weight*maxNodeSize/wm
    bar = Bar('Building network ', max=msize)
    for i in range(0, msize):
        bar.next()
        G.add_node(i, weight=weights[i], label=allAuthors[i])
        for j in range(i+1, msize):
            if edges[i][j] != 0:
                G.add_edge(i, j, weight=edges[i][j]*maxEdgeWidth/edges.max())
    bar.finish()
    # Save graph
    nx.write_graphml(G, out_graphml)

    # Draw graph
    if raw_input('Draw network (y/n)?') == 'y':
        labels = dict((n, d['label']) for (n, d) in G.nodes(data=True))
        edgewidth = [d['weight'] for (u, v, d) in G.edges(data=True)]
        nodesize = [d['weight'] for (u, d) in G.nodes(data=True)]
        pos = nx.spring_layout(G, iterations=100)
        nx.draw_networkx_nodes(G, pos, node_size=nodesize)
        nx.draw_networkx_edges(G, pos, width=0.5, edge_color='b')
        nx.draw_networkx_labels(
            G, pos, labels, alpha=1.0, font_size=3, font_color='black')
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
