#!/usr/bin/env python3

#Author Kelsey Florek
#email kelsey.florek@slh.wisc.edu
#description: generate kmers from a list of paths for each read in order

import os,sys,argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import app.kmer as kmer
import multiprocessing as mp

#setup argparser to display help if no arguments
class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

#returns (num jobs,num cpus per job)
def cpu_count(num):
    if num <=1:
        return 1,1
    elif num <= 5:
        return 1,num
    else:
        results = []
        for n in range(2,num):
            if num % n == 0:
                results.append(n)
        if len(results) < 2:
            return cpu_count(num-1)
        index = int(len(results)/2)
        return results[index],int(num/results[index])

#determine command line arguments and get path
parser = MyParser(description='Generate kmers from all sequencing reads from a file of paths.')

parser.add_argument('file_of_files',help='file with paths to sequencing reads')
parser.add_argument('--db',type=str,help='AR database to use',default='ncbi_ar')
parser.add_argument('-t',type=int,help='number of threads',default=4)
parser.add_argument('-k',type=str,help='k-mer size, default: 7')
parser.add_argument('-o',type=str,help='output directory')

args = parser.parse_args()
reads = []
with open(args.file_of_files,'r') as filepaths:
    line = filepaths.readline()
    while line:
        read1 = line
        read2 = filepaths.readline()
        reads.append([read1,read2])
        line = filepaths.readline()


jobs,cpusJob = cpu_count(args.t)
pool = mp.Pool(processes=jobs)

results = pool.starmap_async(kmer.local_mapping,[[cpusJob,read_pair[0],read_pair[1],args.k,args.db] for read_pair in reads])
files = results.get()
for file in files:
    file_abs = os.path.abspath(file)
    outdir = os.path.abspath(args.o)
    os.rename(file_abs,os.path.join(outdir,file))
    print(f"finished {file}")
'''
for read_pair in reads:
    file = kmer.local_mapping(args.t,read_pair[0],read_pair[1],args.k,args.db)
    file_abs = os.path.abspath(file)
    outdir = os.path.abspath(args.o)
    os.rename(file_abs,os.path.join(outdir,file))
    print(f"finished {file}")
'''
