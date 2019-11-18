#!/usr/bin/env python3

import sys
import pickle

file_list = sys.argv[1]

vocab = {}

c = 0
pathlist = []
with open(file_list,'r') as infile:
    for line in infile.readlines():
        pathlist.append(line.strip())

for file in pathlist:
    with open(file,'r') as infasta:
        for line in infasta.readlines():
            if line[0] != '>':
                seq = line.strip()
                if seq not in vocab:
                    vocab[seq] = c
                    c += 1

with open("kmer_dictionary.pkl",'wb') as outfile:
    pickle.dump(vocab,outfile)
