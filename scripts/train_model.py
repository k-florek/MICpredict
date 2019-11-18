#!/usr/bin/env python3

import csv
import pickle
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from app.chidi import trainModel

#establish global paths
micpredict_path = os.path.dirname(os.path.dirname(os.path.abspath(os.path.realpath(__file__))))
vocab_path = os.path.join(micpredict_path,'db/hf_kmer_dictionary.pkl')

file_paths = sys.argv[1]
mics = sys.argv[2]
flist = []
with open(file_paths,'r') as infile:
    for line in infile.readlines():
        flist.append(line.strip())
mic_data = []
with open(mics,'r') as infile:
    csvr = csv.reader(infile,delimiter=',')
    for line in csvr:
        mic_data.append(line)

with open(vocab_path,'rb') as infile:
    v = pickle.load(infile)
trainModel(flist,v,mic_data)
