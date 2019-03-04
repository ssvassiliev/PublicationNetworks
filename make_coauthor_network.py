#!/usr/bin/python
import bibtexparser
import networkx as nx
import numpy
import matplotlib.pyplot as plt
from math import sqrt
from progress.bar import Bar
from writeNodesEdges import writeObjects
from forceatlas import forceatlas2_layout
#from networkx.algorithms.community import greedy_modularity_communities
#from networkx.algorithms.community import asyn_fluidc
#from networkx.algorithms.community import asyn_lpa_communities
#from networkx.algorithms.community import label_propagation_communities
import community
import igraph as ig


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


def abbrev_auth(auth, db_type):
    # Normalize name records:
    # - strip all names except first, middle and last
    # - abbreviate first and middle names
    # - if initials are joined: 'AA' --> A A
    # - convert to lower case
    t1 = auth.split()
    if db_type == 'scholar':
        if len(t1) > 2:
            ta1 = ' '.join((t1[0][0], t1[1][0], t1[-1]))
        elif len(t1[0]) == 2 and t1[0].isupper():
            ta1 = ' '.join((t1[0][0], t1[0][1], t1[1]))
        else:
            ta1 = ' '.join((t1[0][0], t1[-1]))
    if db_type == 'scopus':
        le = t1[0]
        t1[0] = t1[-1]
        t1[-1] = le
        ta1 = ' '.join(t1).replace(',', '').replace('.', '')
    return(ta1)


if __name__ == "__main__":
    infile = raw_input('Enter name of BibTex file:')
    out_graphml = infile.replace(".bib", ".graphml")
    out_vtk = infile.replace(".bib", "")
    out_bib = infile.replace(".bib", "-edited.bib")
    # Graph parameters
    maxNodeSize = 10
    maxEdgeWidth = 10
    bibtex_file = open(infile)
    bib_str = bibtex_file.read()
    bib_db = bibtexparser.loads(bib_str)
    print('Constructing network from file: ' + infile)
    # Make the list of unique authors
    allAuthors = make_uniq_authors_list(bib_db)
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
    # Add normalized nodes and edges
    wm = weights.max()
    for i, each_weight in enumerate(weights):
        weights[i] = each_weight*maxNodeSize/wm
    bar.finish()

    # NetworkX graph
    do_netX = False
    do_igraph = True
    db_type = 'scholar'
    if do_netX:
        G = nx.Graph()
        bar = Bar('Building networkX graph ', max=msize)
        for i in range(0, msize):
            bar.next()
            G.add_node(i, weight=weights[i],
                       label=abbrev_auth(allAuthors[i], db_type))
            for j in range(i+1, msize):
                if edges[i][j] != 0:
                    G.add_edge(i, j, weight=edges[i][j]*maxEdgeWidth/edges.max())
        bar.finish()
        # Save GRAPHML
        nx.write_graphml(G, out_graphml)
        # Communities
        partitions = [None]*msize
        # communities = list(asyn_fluidc(G, 15, max_iter=200, seed=None))
        # communities = list(asyn_lpa_communities(G, weight=None, seed=None))
        # communities = list(greedy_modularity_communities(G))
        # communities.sort(key=len, reverse=True)
        # for i, comm in enumerate(communities):
        #    for c in comm:
        #        partitions[c] = i
        par = community.best_partition(G)
        partitions = par.values()
        # 3D network layout
        # p = nx.spring_layout(G, iterations=500, dim=3, k=1)
        p = forceatlas2_layout(G, iterations=50, linlog=True, pos=None,
                               nohubs=True, k=None, dim=3)
        # Save VTK
        pos = [list(p[i]) for i in p]
        degree = [d for n, d in G.degree]
        labels = [d['label'] for n, d in G.nodes(data=True)]
        writeObjects(
         pos, edges=G.edges(), nodeLabel=labels,
         scalar=degree, name='degree', power=0.333,
         scalar2=partitions, name2='partition', power2=1.0,
         method='vtkPolyData', fileout=out_vtk)

    # igraph graph
    if do_igraph:
        IG = ig.Graph()
        IG.add_vertices(msize)
        IG.vs['weight'] = weights
        bar = Bar('Building igraph graph ', max=msize)
        auth = []
        eweight = []
        for i in range(0, msize):
            bar.next()
            auth.append(unicode(abbrev_auth(allAuthors[i], db_type)))
            for j in range(i+1, msize):
                if edges[i][j] != 0:
                    IG.add_edge(i, j)
                    eweight.append(edges[i][j]*maxEdgeWidth/edges.max())
        IG.es['weight'] = eweight
        bar.finish()
        # layout = IG.layout("kk3d")
        # 2D layout
        layout2D = IG.layout("fr3d", weights=eweight, area=sqrt(msize))
        layout2D.center()
        IG.vs['x'] = [xy[0] for xy in layout2D.coords]
        IG.vs['y'] = [xy[1] for xy in layout2D.coords]
        IG.vs['label'] = [a.encode('utf-8') for a in auth]
        part = IG.community_multilevel(weights=eweight)
        # Sort partitions by number of sublists
        sorted_part = sorted(part, key=len, reverse=True)
        memb = [0] * msize
        for n, comm in enumerate(sorted_part):
            for i in comm:
                memb[i] = n
        # ig.plot(IG, layout=layout2D)
        # Save
        IG.write_graphml(out_graphml)

        layout3D = IG.layout("fr3d", weights=eweight, area=sqrt(msize))
        layout3D.center()

        # Save VTK
        writeObjects(
         layout3D.coords, edges=IG.get_edgelist(), nodeLabel=auth,
         scalar=list(weights), name='weight', power=0.333,
         scalar2=memb, name2='partition', power2=1.0,
         method='vtkPolyData', fileout=out_vtk)

    # Draw graph
#    if raw_input('Draw network (y/n)?') == 'y':
#        labels = dict((n, d['label']) for (n, d) in G.nodes(data=True))
#        edgewidth = [d['weight'] for (u, v, d) in G.edges(data=True)]
#        nodesize = [d['weight'] for (u, d) in G.nodes(data=True)]
#        pos = nx.spring_layout(G, iterations=100)
#        nx.draw_networkx_nodes(G, pos, node_size=nodesize)
#        nx.draw_networkx_edges(G, pos, width=0.5, edge_color='b')
#        nx.draw_networkx_labels(
#        plt.axis('off')
#        plt.show()

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
