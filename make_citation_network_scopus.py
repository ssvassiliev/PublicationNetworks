#!/usr/bin/python
import bibtexparser
import networkx as nx
import numpy
import matplotlib.pyplot as plt
from progress.bar import Bar


def make_indexed_list_scopus(bib_db):

    def extract_ref_authors_scopus(db_entry):
        references = db_entry['references'].split(';')
        authors = []
        for reference in references:
            title_end_index = reference.find(' (')
            if title_end_index > 3:
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

    all_cit_authors = []
    all_cit_authors_index = []
    global_count = 0
    for entry in bib_db.entries:
        entry_index = []
        all_reference_authors = extract_ref_authors_scopus(entry)
        for ref in all_reference_authors:
            ref_index = []
            for author in ref:
                if author not in all_cit_authors:
                    all_cit_authors.append(author)
                    ref_index.append(global_count)
                    global_count += 1
                else:
                    ref_index.append(all_cit_authors.index(author))
            entry_index.append(ref_index)
        all_cit_authors_index.append(entry_index)
    return(all_cit_authors, all_cit_authors_index)


if __name__ == "__main__":
    # infile = raw_input('Enter name of BibTex file:')
    infile = 'scopus.bib'
    out_graphml = infile.replace(".bib", ".graphml")
    # Graph parameters
    maxNodeSize = 200
    maxEdgeWidth = 3
    bibtex_file = open(infile)
    bib_str = bibtex_file.read()
    bib_db = bibtexparser.loads(bib_str)
    print('Constructing network from file: ' + infile)
    allAuthors, allAuthors_index = make_indexed_list_scopus(bib_db)
    # Create network
    G = nx.Graph()
    msize = len(allAuthors)
    edges = numpy.zeros((msize, msize))
    weights = numpy.zeros(msize)
    # Fill co-citation matrix
    bar = Bar('Processing BibTex', max=len(bib_db.entries))
    for entry in allAuthors_index:
        for reference in entry:
            for author_1 in reference:
                weights[author_1] += 1
                for author_2 in reference:
                    if author_1 != author_2:
                        edges[author_1][author_2] += 1
        bar.next()
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
    print "Drawing may be slow for large networks"
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
