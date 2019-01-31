#!/usr/bin/python
import bibtexparser
import jellyfish
from whoswho import who
import csv
import sys


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
    for i, auth_1 in enumerate(allAuthors):
        for auth_2 in allAuthors[i+1:-1]:
            ta1 = normalize_auth(auth_1, db_type)
            ta2 = normalize_auth(auth_2, db_type)
            djawi_1 = jellyfish.jaro_winkler(ta1, ta2)
            djawi_2 = jellyfish.jaro_winkler(ta1.split()[-1],
                                             ta2.split()[-1])
            if djawi_1 > threshold or djawi_2 > threshold:
                np = np + 1
                while(1):
                    q = auth_1 + ' <---> ' + auth_2 + ' (y/n)?'
                    choice = raw_input(q.encode('ascii', 'ignore'))
                    if choice == 'y':
                        p = (auth_1, auth_2)
                        pairs.append(p)
                        break
                        break
                    elif choice == 'n':
                        break
                    else:
                        continue
    print '---------------------------------'
    print 'Merging: ' + str(len(pairs)) + ' authors'
    return(np, pairs)


def make_pairs_auto(filename, allAuthors, threshold):
    pairs = []
    for i, auth_1 in enumerate(allAuthors):
        for auth_2 in allAuthors[i+1:-1]:
            ta1 = normalize_auth(auth_1, db_type)
            ta2 = normalize_auth(auth_2, db_type)
            djawi_1 = jellyfish.jaro_winkler(ta1, ta2)
            djawi_2 = jellyfish.jaro_winkler(ta1.split()[-1],
                                             ta2.split()[-1])
            if djawi_1 > threshold or djawi_2 > threshold:
                if len(auth_1) < len(auth_2):
                    p = ('n,', auth_1, auth_2, djawi_1, djawi_2)
                else:
                    p = ('n,', auth_2, auth_1, djawi_1, djawi_2)
                pairs.append(p)
    return(pairs)


def save_pairs(pairs, filename):
    f = open(filename, "w+")
    f.write('\n'.join('%s %s, %s, %f, %f' % x for x in pairs).encode('utf-8'))
    f.write('\n')
    f.close()
    return()


def rename_authors(bib_db, pairs):
    for entry in bib_db.entries:
        if 'author' not in entry:
            continue
        for p in pairs:
            if len(p[0]) < len(p[1]):
                entry['author'] = entry['author'].replace(p[1], p[0])
            else:
                entry['author'] = entry['author'].replace(p[0], p[1])
    return(bib_db)


def rename_authors_auto(bib_db, threshold):
    allAuthors = make_uniq_authors_list(bib_db)
    pairs = []
    np = 0
    for i, auth_1 in enumerate(allAuthors):
        for auth_2 in allAuthors[i+1:-1]:
            ta1 = normalize_auth(auth_1, db_type)
            ta2 = normalize_auth(auth_2, db_type)
            # Step 1: Find similar pairs (fast)
            djawi_1 = jellyfish.jaro_winkler(ta1, ta2)
            djawi_2 = jellyfish.jaro_winkler(ta1.split()[-1],
                                             ta2.split()[-1])
            if djawi_1 > threshold or djawi_2 > threshold:
                # Step2 : Do strict person name-specific matching
                if who.match(ta1, ta2):
                    p = (auth_1, auth_2)
                    np = np + 1
                    pairs.append(p)
    # Rename authors according to identified duplicates
    new_db = rename_authors(bib_db, pairs)
    return(np, new_db)


def remove_entries(bib_db, lastname):
    new_db = bibtexparser.bibdatabase.BibDatabase()
    for id, entry in enumerate(bib_db.entries):
        if 'author' not in entry:
            # print entry['ID']
            continue
        elif lastname.lower() not in entry['author'].lower():
            # print entry['ID'] + ' ' + entry['author']
            continue
        else:
            for auth in entry['author'].split(' and '):
                name = auth.split()
                if name[0].strip().lower() == lastname:
                    print "\n** WARNING:** lastname is first in Ref: " \
                     + str(entry['ID']) + " " + str(name) + "\n"
            new_db.entries.append(entry)
    diff = len(bib_db.entries) - len(new_db.entries)
    print 'Removed ' + str(diff) + ' entries missing "' + lastname + '"'
    return(new_db)


def normalize_auth(auth, db_type):
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
    return(ta1.lower())


def read_pairs(filename):
    pairs = []
    with open(filename) as csv_file:
        f = csv.reader(csv_file, delimiter=',')
        for line in f:
            if line[0] == 'y':
                pairs.append(tuple(line[1:3]))
    return(pairs)


reload(sys)
sys.setdefaultencoding('utf8')
# Main program
infile = raw_input('Input BibTex file: ')
db_type = []
while True:
    db_type = raw_input('Database type (scholar/scopus): ')
    if db_type == 'scopus' or db_type == 'scholar':
        break
# infile = 'B.Balcom.bib'
out_bib = infile.replace(".bib", "-edited.bib")
out_pairs = infile.replace(".bib", "-dupl-out.csv")
in_pairs = infile.replace(".bib", "-dupl-in.csv")
# Jaro-Winkler threshold
threshold = 0.9
bibtex_file = open(infile)
bib_str = bibtex_file.read()
bib_db = bibtexparser.loads(bib_str)
print('Cleaning up "' + infile + '"')
# Remove entries not authored by the selected author
lastname = raw_input('Remove entries not authored by (lastname or "enter"):')
# lastname = 'balcom'
new_db = remove_entries(bib_db, lastname)
# Identify and merge duplicate authors programmatically
while(1):
    np, new_db = rename_authors_auto(new_db, threshold)
    if np == 0:
        break
    print 'Merged ' + str(np) + ' duplicate authors'
# Save the list of potential duplicates
allAuthors = make_uniq_authors_list(new_db)
print ' '.join(('The number of authors =', str(len(allAuthors))))
# Merge remaining potential duplicate authors interactively
print ' '.join(('Using Jaro-Winkler algorithm, threshold =', str(threshold)))
pairs = make_pairs_auto(out_pairs, allAuthors, threshold)
print 'The number of remaining potential duplicates = ' + str(len(pairs))
while True:
    allAuthors = make_uniq_authors_list(new_db)
    choice = raw_input(
     '\n'.join(('Merge duplicates:', ' "i" - merge interactively',
                ' "r" - read duplicates from file',
                ' "w" - write duplicates to file and finish', '>>>')))
    print ''
    if choice == 'i':
        np, pairs = make_pairs(allAuthors, threshold)
        if np == 0:
            break
        rename_authors(new_db, pairs)
    elif choice == 'w':
        pairs = make_pairs_auto(out_pairs, allAuthors, threshold)
        save_pairs(pairs, out_pairs)
        print 'Duplicates are written to file ' + out_pairs
        break
    elif choice == 'r':
        print 'Reading duplicates from file ' + in_pairs
        pairs = read_pairs(in_pairs)
        while(1):
            old_np = len(allAuthors)
            rename_authors(new_db, pairs)
            allAuthors = make_uniq_authors_list(new_db)
            diff = old_np - len(allAuthors)
            if diff == 0:
                break
            print 'Merged ' + str(diff) + ' authors'
        break
    else:
        continue
# Save the edited bibtex file
with open(out_bib, 'w') as bibtex_file:
    bibtexparser.dump(new_db, bibtex_file)
print 'Saved ' + out_bib
