#!/usr/bin/env python3

#Author Kelsey Florek
#email kelsey.florek@slh.wisc.edu
#generate kmers from a list of paths for each read in order

import os,sys,argparse
import app.kmer as kmer

#setup argparser to display help if no arguments
class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

#determine command line arguments and get path
parser = MyParser(description='Generate kmers from all sequencing reads from a file of paths.')

parser.add_argument('file_of_files',help='file with paths to sequencing reads')
parser.add_argument('--db',type=str,help='AR database to use',default='ncbi_ar')
parser.add_argument('-t',type=int,help='number of threads',default=4)

args = parser.parse_args()
reads = []
with open(args.file_of_files,'r') as filepaths:
    line = filepaths.readline()
    while line:
        read1 = line
        read2 = filepaths.readline()
        reads.append([read1,read2])
        line = filepaths.readline()

for read_pair in reads:
    kmer.local_mapping(args.t,read_pair[0],read_pair[1],args.db)
