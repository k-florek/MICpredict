#!/usr/bin/env python3
import os,sys
import tensorflow as tf
from tensorflow import keras
import csv
import numpy as np
import pickle

def trainModel(kmer_paths,vocab,mic_values):
    train_array = np.zeros((len(kmer_paths),len(vocab)),dtype=int)
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
                train_labels[label_row] = row
                break
        label_row += 1

    #define the RNN model for 7-mer
    model = tf.keras.Sequential([
    # Adds a densely-connected layer with 64 units to the model:
    layers.Dense(8192, activation='relu', input_shape=(32,)),
    #add a drop layer
    layers.Dropout(0.5),
    # Add another:
    layers.Dense(4096, activation='relu'),
    #add a drop layer
    layers.Dropout(0.5),
    # Add an output layer with 10 output units:
    layers.Dense(28)])

    #create the model
    model.compile(optimizer=tf.keras.optimizers.Adam(),
                  loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    #train the model
    print('Training the random forest model.')
    model.fit(train_array, train_labels, epochs=10, batch_size=32)

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
