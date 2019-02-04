#!/usr/bin/python
import tkFileDialog
import Tkinter as tk
import ttk
import tkMessageBox
from make_coauthor_network import make_uniq_authors_list
from make_citation_network_scopus import make_indexed_list_scopus
import bibtexparser
import networkx as nx
import numpy


def citation_network():
    # Max number of progress bar increments
    nbar = 50
    infile = filename.get()
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
    ii = 0.0
    asize = len(allAuthors_index)
    for i, entry in enumerate(allAuthors_index):
        for reference in entry:
            for author_1 in reference:
                weights[author_1] += 1
                for author_2 in reference:
                    if author_1 != author_2:
                        edges[author_1][author_2] += 1
        # ---- Update progress bar ----
        ii += 1
        if asize < 4*nbar:
            pb2['value'] = (i+1)*100.0/asize
            pb2.update()
        else:
            if ii >= asize/nbar or i+1 == asize:
                ii = 0.0
                pb2['value'] = (i+1)*100.0/asize
                pb2.update()
        # --- Update progress bar end ---
    # Add normalized nodes and edges
    wm = weights.max()
    for i, each_weight in enumerate(weights):
        weights[i] = each_weight*maxNodeSize/wm
    ii = 0.0
    for i in range(0, msize):
        # ---- Update progress bar ----
        ii += 1
        if msize < 4*nbar:
            pb['value'] = (i+1)*100.0/msize
            pb.update()
        else:
            if ii >= msize/nbar or i+1 == msize:
                ii = 0.0
                pb['value'] = (i+1)*100.0/msize
                pb.update()
        # --- Update progress bar end ---
        G.add_node(i, weight=weights[i], label=allAuthors[i])
        for j in range(i+1, msize):
            if edges[i][j] != 0:
                G.add_edge(i, j, weight=edges[i][j]*maxEdgeWidth/edges.max())
    # Save graph
    nx.write_graphml(G, out_graphml)
    return(G.number_of_nodes(), G.number_of_edges())


def co_author_network():
    # Max number of progress bar increments
    nbar = 50
    infile = filename.get()
    out_graphml = infile.replace(".bib", ".graphml")
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
    asize = len(bib_db.entries)
    ii = 0
    for i_ent, entry in enumerate(bib_db.entries):
        ii += 1
        # Update progress bar every step
        if asize < 4*nbar:
            pb2['value'] = (i_ent+1)*100.0/asize
            pb2.update()
        else:
            if ii >= asize/nbar or i_ent+1 == asize:
                ii = 0.0
                pb2['value'] = (i_ent+1)*100.0/asize
                pb2.update()
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
    ii = 0.0
    for i in range(0, msize):
        ii += 1
        # Update progress bar every step
        if msize < 4*nbar:
            pb['value'] = (i+1)*100.0/msize
            pb.update()
        else:
            if ii >= msize/nbar or i+1 == msize:
                ii = 0.0
                pb['value'] = (i+1)*100.0/msize
                pb.update()
        G.add_node(i, weight=weights[i], label=allAuthors[i])
        for j in range(i+1, msize):
            if edges[i][j] != 0:
                G.add_edge(i, j, weight=edges[i][j]*maxEdgeWidth/edges.max())
    # Save graph
    nx.write_graphml(G, out_graphml)
    print 'Number of edges = ' + str(G.number_of_edges())
    print 'Number of nodes = ' + str(G.number_of_nodes())
    return(G.number_of_nodes(), G.number_of_edges())


def select_file():
    blank = "no file selected"
    f = tkFileDialog.askopenfilename(
     initialdir="./", title="Select file",
     filetypes=(("BibTex files", "*.bib"), ("all files", "*.*")))
    s = str(f).split('/')[-1]
    if len(f) < 5:
        filename.set('')
        flabel.set(blank)
    else:
        filename.set(f)
        flabel.set(s)
    return()


def make_network():

    def tklabel(nd, ed):
        nde = ''.join(("Number of nodes = ", str(nd),
                       "\nNumber of edges = ", str(ed)))
        nodedge.set(nde)
    if str(filename.get()) == '':
        tkMessageBox.showerror(
         "IOError", ''.join(("Please select file")))
        return()

    pb['value'] = 0
    pb2['value'] = 0
    nodedge.set("Number of nodes = 0\nNumber of edges = 0")
    pb.update()
    pb2.update()
    # database type
    dbt = db_type.get()
    # network type
    nwt = net_type.get()
    # co-authorship network extraction works for both database types
    if nwt == 0:
        nd, ed = co_author_network()
        tklabel(nd, ed)
    # co-citaion network extraction works with Scopus files
    if nwt == 1 and dbt == 1:
        try:
            nd, ed = citation_network()
            tklabel(nd, ed)
        except KeyError, e:
            tkMessageBox.showerror(
             "KeyError", ''.join(("File has no ", str(e), " record")))
            return()
    # co-citaion network extraction does not work with Scholar files
    if nwt == 1 and dbt == 0:
            tkMessageBox.showerror(
             "DataBaseTypeError",
             "Co-citation network cannot be made from Google Scholar files")
            return()


if __name__ == "__main__":
    blank = "no file selected"
    root = tk.Tk()
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("TProgressbar", foreground='red',
                background='red', thickness=5)
    db_type = tk.IntVar()
    net_type = tk.IntVar()
    filename = tk.StringVar()
    flabel = tk.StringVar()
    nodes = tk.StringVar()
    edges = tk.StringVar()
    nodedge = tk.StringVar()
    flabel.set(blank)
    nodedge.set("Number of nodes = 0\nNumber of edges = 0")

    # Root window
    root.title('Network Extractor')
    root["padx"] = 20
    root["pady"] = 20
    # Select database type
    tk.Label(root, text="Database type:",
             padx=20).grid(row=0, column=1, sticky=tk.W)
    tk.Radiobutton(root, text="Scholar", padx=10, variable=db_type,
                   value=0).grid(row=1, column=1, sticky=tk.W)
    tk.Radiobutton(root, text="Scopus", padx=10, variable=db_type,
                   value=1).grid(row=2, column=1, sticky=tk.W)
    # Select network type
    tk.Label(root, text="Network type:",
             padx=20).grid(row=0, column=2, sticky=tk.W)
    tk.Radiobutton(root, text="Co-authorship", padx=10, variable=net_type,
                   value=0).grid(row=1, column=2, sticky=tk.W)
    tk.Radiobutton(root, text="Co-citation", padx=10, variable=net_type,
                   value=1).grid(row=2, column=2, sticky=tk.W)
    # Select BibTex file
    tk.Button(root, text="Select .bib file", width=12,
              command=select_file).grid(row=3, column=0, columnspan=1,
                                        pady=5, sticky=tk.W)
    tk.Label(root, textvariable=flabel, padx=5,
             ).grid(row=3, column=1, columnspan=1, sticky=tk.W)
    # Extract network
    tk.Button(root, text="Make network", width=12,
              command=make_network).grid(row=4, column=0, columnspan=1,
                                         pady=2, sticky=tk.W)
    # Progress bar 1
    pb = ttk.Progressbar(root, orient='horizontal',
                         mode='determinate', length=200)
    pb.grid(row=4, column=1, columnspan=1, sticky=tk.S+tk.W)
    pb["value"] = 0
    pb["maximum"] = 100
    # Progress bar 2
    pb2 = ttk.Progressbar(root, orient='horizontal',
                          mode='determinate', length=200)
    pb2.grid(row=4, column=1, columnspan=1, sticky=tk.N+tk.W)
    pb2["value"] = 0
    pb2["maximum"] = 100
    # Print results
    tk.Label(root, text="Info:", padx=20,
             ).grid(row=5, column=0, columnspan=1, sticky=tk.E)
    tk.Label(root, textvariable=nodedge, justify=tk.LEFT,
             ).grid(row=5, column=1, columnspan=1, sticky=tk.W)
    # Quit
    tk.Button(root, text="Quit", fg='black', justify=tk.LEFT,
              command=exit).grid(row=5, column=2, columnspan=1,
                                 pady=5, padx=10, sticky=tk.E)

#    text = tk.Text(root)
#    text.insert(tk.INSERT, "Hello.....")
#    text.grid(row=5, column=0, columnspan=2,
#              pady=5, padx=10, sticky=tk.W)

    root.mainloop()
