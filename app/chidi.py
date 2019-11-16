#!/usr/bin/env python3
import os,sys
from sklearn.ensemble import RandomForestClassifier as RFC
import csv
import json
import numpy as np
import pickle

def trainModel(kmer_paths,vocab,mic_values):
    train_array = np.zeros((len(kmer_paths),8000000),dtype=int)
    train_ids = []

    #read convert and store kmers
    row = 0
    for file in kmer_paths:
        current_id =os.path.basename(file).split('.')[0]
        print("Adding: "+current_id)
        train_ids.append(current_id)

        with open(file,'r') as inkmer:
            line = inkmer.readline()
            while line:
                num_ks = int(line[1:])
                seq = inkmer.readline().strip()
                k_id = vocab[seq]
                train_array[row,k_id] = num_ks
                line = inkmer.readline()

        row += 1

    #pull and order mic values
    train_labels = np.empty((len(kmer_paths),28),dtype=np.dtype("U10"))
    label_row = 0
    for id in train_ids:
        for row in mic_values:
            if row[1] in id:
                train_labels[label_row] = row[3:]
                break
        label_row += 1

    #train the model
    print('Training the random forest model.')
    clf = RFC(n_estimators=10,random_state=22,n_jobs=-1,verbose=1)
    clf.fit(train_array,train_labels)

    #save the model
    with open("rf_model.sav",'wb') as model_file:
        pickle.dump(clf,model_file)

def predict(kmer_paths,vocab,model_path):
    predict_array = np.zeros((len(kmer_paths),8000000),dtype=int)
    predict_ids = []

    #read convert and store kmers
    row = 0
    for file in kmer_paths:
        current_id =os.path.basename(file).split('.')[0]
        print("Adding: "+current_id)
        predict_ids.append(current_id)

        with open(file,'r') as inkmer:
            line = inkmer.readline()
            while line:
                num_ks = int(line[1:])
                seq = inkmer.readline().strip()
                k_id = vocab[seq]
                predict_array[row,k_id] = num_ks
                line = inkmer.readline()

        row += 1
    with open(model_path,'rb') as model_file:
        clf = pickle.load(model_file)
    result = clf.predict(predict_array)
    return predict_ids,result
