#!/usr/bin/env python3

#Author Kelsey Florek
#email kelsey.florek@slh.wisc.edu
#description: generate kmers from a list of paths for each read in order

import os,sys,argparse,shutil
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import app.kmer as kmer
import multiprocessing as mp
import glob

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

parser.add_argument('path_of_fastq',help='path to fastq_files')
parser.add_argument('--db',type=str,help='AR database to use, default ncbi_ar',default='ncbi_ar')
parser.add_argument('-t',type=int,help='number of threads',default=4)
parser.add_argument('-k',type=str,help='k-mer size, default: 7',default='7')
parser.add_argument('-o',type=str,help='output directory')

args = parser.parse_args()

#get arguments
jobs,cpusJob = cpu_count(args.t)
pool = mp.Pool(processes=jobs)

#check out dir
try:
    os.mkdir(args.o)
except FileExistsError:
    print("Output Directory already exists.")
    sys.exit(1)

#get fwd and rev reads
fwd_reads = glob.glob(os.path.join(args.path_of_fastq,'*_R1*.fastq.gz'))
fwd_reads.sort()
rev_reads = glob.glob(os.path.join(args.path_of_fastq,'*_R2*.fastq.gz'))
rev_reads.sort()

#Define error catching for fastq input
class InputError(Exception):
    def __init__(self,error_msg):
        self.error_msg = error_msg
    def __str__(self):
        return self.error_msg

#Check if we have even number of paired reads
if len(fwd_reads) != len(rev_reads):
    raise InputError("There is an uneven number of fastq files on input.")

#combine fastq_files
counter = 0
read_pairs = []
while counter < len(fwd_reads):
    #check we have a pair
    if fwd_reads[counter].split('_R1')[0] == rev_reads[counter].split('_R2')[0]:
        read_pairs.append([os.path.abspath(fwd_reads[counter]),os.path.abspath(rev_reads[counter])])
    else:
        raise InputError("Mismatch Read Pair: "+fwd_reads[counter]+" and "+rev_reads[counter])
    counter += 1

#create dir for holding temp files
try:
    os.mkdir("MICpredict_kmer_temp_files")
except FileExistsError:
    temp_dir = os.path.abspath("MICpredict_kmer_temp_files")
    shutil.rmtree(temp_dir)
    os.mkdir("MICpredict_kmer_temp_files")
temp_dir = os.path.abspath("MICpredict_kmer_temp_files")

results = pool.starmap_async(kmer.local_mapping,[[cpusJob,read_pair[0],read_pair[1],args.k,args.db,temp_dir] for read_pair in read_pairs])
files = results.get()
for file in files:
    file_abs = os.path.join(temp_dir,file)
    outdir = os.path.abspath(args.o)
    os.rename(file_abs,os.path.join(outdir,file))
    print(f"finished {file}")

shutil.rmtree(temp_dir)
