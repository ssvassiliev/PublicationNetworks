#!/usr/bin/python
import tkFileDialog
import Tkinter as tk
import ttk
import tkMessageBox
from make_coauthor_network import make_uniq_authors_list
from make_citation_network_scopus import make_indexed_list_scopus
from edit_authors import remove_entries, rename_authors_auto, make_pairs_auto,\
 rename_authors, save_pairs
import bibtexparser
import networkx as nx
import numpy
import sys
from sys import exit


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
    print 'number of edges = ' + str(G.number_of_edges())
    print 'number of nodes = ' + str(G.number_of_nodes())
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
        nde = ''.join(("number of nodes = ", str(nd),
                       "\nnumber of edges = ", str(ed)))
        nodedge.set(nde)
    if str(filename.get()) == '':
        tkMessageBox.showerror(
         "IOError", ''.join(("Please select file")))
        return()

    pb['value'] = 0
    pb2['value'] = 0
    nodedge.set("number of nodes = 0\nnumber of edges = 0")
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


def edit_authors(stage):
    if stage == 1:
        print "stage 1"
    if stage == 2:
        print "stage 2"
    reload(sys)
    sys.setdefaultencoding('utf8')
    infile = filename.get()
    dbt = db_type.get()
    if dbt == 0:
        dbType = "scholar"
    if dbt == 1:
        dbType = "scopus"
    # infile = 'B.Balcom.bib
    out_bib = infile.replace(".bib", "-edited.bib")
    out_pairs = infile.replace(".bib", "-dupl.csv")
    # Jaro-Winkler threshold
    threshold = 0.9
    if stage == 1:
        bibtex_file = open(infile)
        bib_db = bibtexparser.load(bibtex_file)
        # Remove entries not authored by the selected author
        lastName = lastname.get()
        removed, new_db = remove_entries(bib_db, lastName)
        infoMessage0 = ' '.join((
            "Removed entries:", str(removed)))
        # Identify and merge duplicate authors programmatically
        infoMessage1 = ''.join(('File: "', infile.split('/')[-1], '"'))
        infoMessage2 = ''
        snp = 0
        while True:
            np, new_db = rename_authors_auto(new_db, threshold, dbType)
            snp += np
            if np == 0:
                break
        infoMessage2 = ''.join(('\nMerged authors: ', str(snp)))

        # Save the list of potential duplicates
        allAuthors = make_uniq_authors_list(new_db)
        pairs = make_pairs_auto(out_pairs, allAuthors, threshold, dbType)

        infoMessage3 = ' '.join((
            '\nTotal authors:', str(len(allAuthors)),
            '\nDuplicate authors: ', str(len(pairs))))
        save_pairs(pairs, out_pairs)
        pairs_csv = (
         '\n'.join('%s %s, %s, %f, %f' % x for x in pairs).encode('utf-8'))
        duPairs.set(pairs_csv)
        infoMessage4 = ''.join(('\nSaved: "', out_pairs.split('/')[-1],
                                '"'))
        print infoMessage1 + infoMessage2 + infoMessage3 + infoMessage4
        messageInfo1.set(infoMessage0 + infoMessage2 + infoMessage3)
        bibtex_str.set(bibtexparser.dumps(new_db))
    if stage == 2:
        text = bibtex_str.get()
        new_db = bibtexparser.loads(text)
        ps = duPairs.get()
        pt = ps.split('\n')
        pairs = []
        for line in pt:
            li = line.split(',')
            if li[0] == 'y':
                pairs.append(tuple(li[1:3]))
        snp = 0
        while True:
            np, new_db = rename_authors(new_db, pairs)
            snp += np
            if np == 0:
                break
        infoMessage2 = ''.join(('\nMerged authors: ', str(snp)))
        # Save the edited bibtex file
        with open(out_bib, 'w') as bibtex_file:
            bibtexparser.dump(new_db, bibtex_file)
        print 'Saved ' + out_bib


if __name__ == "__main__":
    blank = "no file selected"
    root = tk.Tk()
    n = ttk.Notebook(root)
    f2 = ttk.Frame(n)
    f1 = ttk.Frame(n)
    n.grid(row=1, column=0, columnspan=50, rowspan=49, sticky='NESW')
    n.add(f1, text='Edit BibTex')
    n.add(f2, text='Network')
    # root.geometry("400x350")
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("TProgressbar", foreground='red',
                background='red', thickness=4)
    db_type = tk.IntVar()
    bibtex_str = tk.StringVar()
    net_type = tk.IntVar()
    filename = tk.StringVar()
    lastname = tk.StringVar()
    flabel = tk.StringVar()
    messageInfo1 = tk.StringVar()
    duPairs = tk.StringVar()
    nodes = tk.StringVar()
    edges = tk.StringVar()
    text = tk.StringVar()
    nodedge = tk.StringVar()
    flabel.set(blank)
    nodedge.set("number of nodes = 0\nnumber of edges = 0")

    def pair_editor():

        def save_text():
            P = t.get(1.0, tk.END)
            duPairs.set(P)
            win.destroy()

        win = tk.Toplevel(f1)
        ybar = tk.Scrollbar(win)
        t = tk.Text(win)
        ybar.config(command=t.yview)
        t.config(yscrollcommand=ybar.set)
        t.grid(row=0, column=0)
        t.delete(1.0, tk.END)
        t.insert(tk.END, duPairs.get())
        tk.Button(win, text="OK", command=save_text).grid(
         row=1, column=0, columnspan=1, pady=10, padx=1, sticky='ne')
        ybar.grid(row=0, column=1, sticky="ns")

    root.title('Network Extractor')
    root["padx"] = 20
    root["pady"] = 20
    # Make Network Window
    # -----------------------------------------
    # Select BibTex file
    c3 = [0, 1]
    r3 = [0, 0]
    tk.Button(f2, text="Select File", width=9, takefocus=0,
              command=select_file).grid(row=r3[0], column=c3[0], columnspan=1,
                                        pady=10, padx=1, sticky='ne')
    tk.Label(f2, textvariable=flabel, padx=5
             ).grid(row=r3[1], column=c3[1], columnspan=1, sticky=tk.W)
    # Select database type
    c1 = [0, 0, 0]
    r1 = [1, 2, 3]
    tk.Label(f2, text="Database type:",
             padx=20, pady=5).grid(row=r1[0], column=c1[0], sticky='nw')
    tk.Radiobutton(f2, text="Scholar", padx=20, variable=db_type, takefocus=0,
                   value=0).grid(row=r1[1], column=c1[1], sticky='nw')
    tk.Radiobutton(f2, text="Scopus", padx=20, variable=db_type, takefocus=0,
                   value=1).grid(row=r1[2], column=c1[2], sticky='nw')
    # Select network type
    c2 = [1, 1, 1]
    r2 = [1, 2, 3]
    tk.Label(f2, text="Network type:",
             padx=20, pady=5).grid(row=r2[0], column=c2[0], sticky='nw')
    tk.Radiobutton(
     f2, text="Co-authorship", padx=20, variable=net_type, takefocus=0,
     value=0).grid(row=r2[1], column=c2[1], sticky='nw')
    tk.Radiobutton(
     f2, text="Co-citation", padx=20, pady=5, variable=net_type, takefocus=0,
     value=1).grid(row=r2[2], column=c2[2], sticky='nw')
    ttk.Separator(f2, orient=tk.HORIZONTAL).grid(
        column=0, row=4, columnspan=3, pady=10, sticky='nwe')
    # Make network
    tk.Button(
     f2, text="Make Network", width=12, pady=5, padx=1, takefocus=0,
     command=make_network).grid(row=5, column=0, columnspan=1, sticky='se')
    # Progress bar 1
    pb = ttk.Progressbar(f2, orient='horizontal',
                         mode='determinate', length=180)
    pb.grid(row=5, column=1, columnspan=1, sticky=tk.S+tk.W)
    # Progress bar 2
    pb2 = ttk.Progressbar(f2, orient='horizontal',
                          mode='determinate', length=180)
    pb2.grid(row=5, column=1, columnspan=1, sticky=tk.N+tk.W)
    # Print network properties
    tk.Label(f2, text="Network\nproperties:",  padx=20,
             ).grid(row=7, column=0, columnspan=1, sticky=tk.E)
    tk.Label(f2, textvariable=nodedge, justify=tk.LEFT,
             ).grid(row=7, column=1, columnspan=1, sticky=tk.W)
    # Quit Button
    tk.Button(f2, text="Quit", fg='black', justify=tk.LEFT, takefocus=0,
              command=exit).grid(row=8, column=2, columnspan=1,
                                 pady=5, padx=1, sticky=tk.E)

    # Edit BibTex Window
    # ---------------------------------------
    # Select BibTex file
    c3 = [0, 1]
    r3 = [0, 0]
    tk.Button(f1, text="Select File", width=9, takefocus=0,
              command=select_file).grid(row=r3[0], column=c3[0], columnspan=1,
                                        pady=10, sticky='nw')
    tk.Label(f1, textvariable=flabel, padx=5
             ).grid(row=r3[1], column=c3[1], columnspan=1, sticky=tk.W)
    # Select database type
    c1 = [0, 0, 0]
    r1 = [1, 2, 3]
    tk.Label(f1, text="Database type:",
             padx=1, pady=5).grid(row=r1[0], column=c1[0], sticky='nw')
    tk.Radiobutton(f1, text="Scholar", padx=1, variable=db_type, takefocus=0,
                   value=0).grid(row=r1[1], column=c1[1], sticky='nw')
    tk.Radiobutton(f1, text="Scopus", padx=1, variable=db_type, takefocus=0,
                   value=1).grid(row=r1[2], column=c1[2], sticky='nw')
    # Lastname of the principal author entry
    c2 = [1, 1, 1]
    r2 = [1, 2, 3]
    tk.Label(f1, text="Remove entries\nnot authored by:",
             padx=1, pady=5).grid(row=r2[0], column=c2[0], sticky='nw')
    tk.Entry(
     f1, textvariable=lastname).grid(row=r2[1], column=c2[1], sticky='nw')
    ttk.Separator(f1, orient=tk.HORIZONTAL).grid(
        column=0, row=4, columnspan=3, pady=10, sticky='nwe')
    # Auto cleanup
    tk.Button(
     f1, text="Auto cleanup", width=14, command=lambda: edit_authors(1),
     takefocus=0,).grid(row=5, column=0, columnspan=1, sticky='w')
    # Print autocleanup info
    l1 = tk.Label(f1, textvariable=messageInfo1, justify=tk.LEFT)
    l1.grid(row=5, rowspan=4, column=1,  padx=10, sticky='nw')
    # Select duplicates
    tk.Button(
     f1, text="Select duplicates", fg='black', justify=tk.LEFT, takefocus=0,
     command=pair_editor).grid(row=6, column=0, columnspan=1, sticky='sw')
    # Save BibTex
    tk.Button(
     f1, text="Save BibTex", width=14, command=lambda: edit_authors(2),
     takefocus=0,).grid(row=7, column=0, columnspan=1, sticky='w')
    # Quit Button
    tk.Button(f1, text="Quit", fg='black', justify=tk.LEFT, takefocus=0,
              command=exit).grid(row=7, column=2, columnspan=1,
                                 pady=5, padx=10, sticky='se')
    root.mainloop()
