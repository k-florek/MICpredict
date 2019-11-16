#!/usr/bin/env python3
from .app.chidi import trainModel
import csv
import json
import os,sys

#establish global paths
salomic_path = os.path.dirname(os.path.dirname(os.path.abspath(os.path.realpath(__file__))))
vocab_path = os.path.join(salomic_path,'db/kmer_dictionary.json')

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

with open(vocab_path,'r') as infile:
    v = json.load(infile)
trainModel(flist,v,mic_data)
