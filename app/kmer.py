#Author Kelsey Florek
#email kelsey.florek@slh.wisc.edu
#description: generate the kmers used in the model

import os,sys,shlex
from subprocess import Popen, PIPE, DEVNULL
import random
from app.qta import qta
import csv
from glob import glob

#establish global paths
micpredict_path= os.path.dirname(os.path.dirname(os.path.abspath(os.path.realpath(__file__))))
binaries_path = os.path.join(micpredict_path,'binaries/linux/')

#function to map reads to ncbi resistance database
def local_mapping(cpus,read1,read2,kmer='7',database='ncbi_ar',working_dir='.'):
    #goto working_dir
    work_dir_path = os.path.abspath(working_dir)
    os.chdir(work_dir_path)

    #establish absoulte paths to everything we need
    seqid = os.path.basename(read1).split('_R1')[0]
    database_path = os.path.join(*[micpredict_path,'db',database])
    fasta_seq_pos = {}
    print(f"Processing kmers for {seqid}")

    #generate a name for the temp files
    temp_name = seqid+str(random.randint(1000,10000000))

    #decompress reads and convert to fasta
    print('Running decompression...')
    decompress_read1 = f"pigz -dc -p {cpus} {read1}"
    decompress_read2 = f"pigz -dc -p {cpus} {read2}"
    decompress_read1_cmd = shlex.split(decompress_read1)
    decompress_read2_cmd = shlex.split(decompress_read2)

    with open(temp_name+".fasta","w") as outfasta:
        p = Popen(decompress_read1_cmd,stdout=PIPE)
        pos = outfasta.tell()
        for line in qta(p.stdout,'_r1'):
            if line[0] == '>':
                fasta_seq_pos[line[1:].strip()] = pos
            outfasta.write(line)
            pos = outfasta.tell()
        p = Popen(decompress_read2_cmd,stdout=PIPE)
        pos = outfasta.tell()
        for line in qta(p.stdout,'_r2'):
            if line[0] == '>':
                fasta_seq_pos[line[1:].strip()] = pos
            outfasta.write(line)
            pos = outfasta.tell()

    #build blast database
    print('Building database...')
    makeblastdb_path = os.path.join(binaries_path,'makeblastdb')
    buildblastdb = f"{makeblastdb_path} -in {temp_name}.fasta -dbtype nucl -out {temp_name}"
    buildblastdb_cmd = shlex.split(buildblastdb)
    Popen(buildblastdb_cmd,stdout=DEVNULL,env={'PATH':binaries_path}).wait()

    #run blast
    print('Running blastn...')
    blastn_path = os.path.join(binaries_path,'blastn')
    runblast = f"{blastn_path} -num_threads {cpus} -query {database_path} -db {temp_name} -out {temp_name}.blast.csv -outfmt \"10 qseqid sseqid evalue pident\" -max_target_seqs 10000000 -evalue 100"
    runblast_cmd = shlex.split(runblast)
    Popen(runblast_cmd,stdout=DEVNULL,env={'PATH':binaries_path}).wait()

    #filter fasta by blast results
    print('Filtering fasta...')
    pulled_reads = []
    with open(f"{temp_name}.blast.csv",'r') as inmatches:
        matches = csv.reader(inmatches,delimiter=',')
        with open(f"{temp_name}.matches.fasta",'w') as outfasta:
            with open(f"{temp_name}.fasta",'r') as infasta:
                for row in matches:
                    id = row[1]
                    if not id in pulled_reads:
                        pulled_reads.append(id)
                        infasta.seek(fasta_seq_pos[id])
                        outfasta.write(infasta.readline())
                        outfasta.write(infasta.readline())

    #generate kmers
    print('Generating Kmers...')
    jellyfish_path = os.path.join(binaries_path,'jellyfish')
    count_kmers = f"{jellyfish_path} count -m {kmer} -s 100M -t {cpus} -C {temp_name}.matches.fasta -o {temp_name}"
    count_kmers_cmd = shlex.split(count_kmers)
    Popen(count_kmers_cmd,stdout=DEVNULL,env={'PATH':binaries_path,'LD_LIBRARY_PATH':binaries_path}).wait()
    dump_kmers = f"{jellyfish_path} dump {temp_name}_0"
    dump_kmers_cmd = shlex.split(dump_kmers)
    with open(f"{seqid}.kmers.fa",'w') as outkmers:
        Popen(dump_kmers_cmd,stdout=outkmers,env={'PATH':binaries_path,'LD_LIBRARY_PATH':binaries_path}).wait()

    #remove temp files
    file_list = glob(f'{temp_name}*')
    for file in file_list:
       os.remove(file)

    return f"{seqid}.kmers.fa"
