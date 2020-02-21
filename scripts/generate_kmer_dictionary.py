#!/usr/bin/env python3

import sys
import itertools
import pickle
import argparse

#setup argparser to display help if no arguments
class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

parser = MyParser(description='Get all possible kmers.')

parser.add_argument('k',help='length of k-mer')
args = parser.parse_args()

k = int(args.k)

DNAchars = 'ATGC'
vocab = {}
for kmer_l in itertools.product(DNAchars,repeat=k):
    kmer = ''.join(kmer_l)
    vocab[kmer] = 0

print("Generated dictionary of length:",len(vocab))
with open(f'{k}-mer_dictionary_len-{len(vocab)}.pkl','wb') as outfile:
    pickle.dump(vocab,outfile)
