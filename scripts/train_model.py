#!/usr/bin/env python3

import csv
import pickle
import os,sys, glob
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from app.forcett import trainModel

#establish global paths
micpredict_path = os.path.dirname(os.path.dirname(os.path.abspath(os.path.realpath(__file__))))

#setup argparser to display help if no arguments
class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

parser = MyParser(description='Train the RNN Model.')

parser.add_argument('kmer_dir',help='directory containing kmer fasta files')
parser.add_argument('mic_csv',help='Mic Values in CSV format')
parser.add_argument('kmer_dictionary',help='Kmer dictionary generated from generate_kmer_dictionary.py')
args = parser.parse_args()

kmer_fasta_list = glob.glob(os.path.join(args.kmer_dir,'*.kmers.fa'))

with open(args.kmer_dictionary,'rb') as infile:
    vocab = pickle.load(infile)

trainModel(kmer_fasta_list,vocab,args.mic_csv)
