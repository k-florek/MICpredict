#!/usr/bin/env python3
import os,sys
import tensorflow as tf
from tensorflow import keras
import csv
import numpy as np
import pandas
import pickle
import itertools
from sklearn.preprocessing import LabelEncoder

def trainModel(kmer_paths,vocab,mic_csv):
    gpus = tf.config.experimental.list_physical_devices('GPU')
    tf.config.experimental.set_memory_growth(gpus[0], True)
    tf.get_logger().setLevel('INFO')

    #setup training array
    train_array = pandas.DataFrame()

    #get mic data into numpy array
    mic_data = pandas.read_csv(mic_csv)

    #read convert and store kmers
    print("############")
    print("Building Trainning Array")
    print("############")
    input_dataset = {}
    for seq_id in mic_data['PulseNet WGS ID']:
        for file in kmer_paths:
            if seq_id in file:
                #print("Adding: "+seq_id+" from "+file+" total is: "+str(row))
                hash_check = []
                input_dataset[seq_id] = []
                with open(file,'r') as inkmer:
                    line = inkmer.readline()
                    while line:
                        num_ks = int(line[1:])
                        seq = inkmer.readline().strip()
                        kmer_hash = tf.keras.preprocessing.text.hashing_trick(seq,100000000000,'md5')[0]
                        if kmer_hash not in hash_check:
                            hash_check.append(kmer_hash)
                        else:
                            print("Warning: kmer collision: "+seq+" with hash "+str(kmer_hash))
                        input_dataset[seq_id].append((kmer_hash,num_ks))
                        line = inkmer.readline()
                break
    #convert to numpy array
    temp_list = []
    for key in input_dataset:
        temp_list.append(input_dataset[key])
    input_array = np.array(temp_list)

    #integer encode training labels
    train_labels = mic_data.loc[:,"AMOC":]
    #get unique values for fit model
    unique_values = []
    for col in train_labels:
        for item in train_labels[col].unique():
            if item not in unique_values:
                unique_values.append(item)
    unique_values.sort()
    label_encoder = LabelEncoder()
    label_encoder.fit(unique_values)

    #encode the labels and convert to numpy array
    for col in train_labels:
        train_labels[col]= label_encoder.transform(train_labels[col])
    encoded_labels = train_labels.to_numpy()

    #set batch size
    batch_size = 32

    #define the RNN model for 7-mer
    model = keras.Sequential([
    tf.keras.layers.Dense(1024, input_shape=(len(input_array[1]),)),
    #Bidirectional layer
    tf.keras.layers.Dropout(0.4),
    # Adds a densely-connected layer with 64 units to the model:
    tf.keras.layers.Dense(128, activation='relu'),
    # Add an output layer with 28 output units:
    keras.layers.Dense(28)])

    #create the model
    model.compile(optimizer=keras.optimizers.Adam(),
                  loss=keras.losses.CategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    #train the model
    print('Training the model.')
    history = model.fit(train_array,encoded_labels,batch_size=batch_size,validation_split=0.1, epochs=10)
    print(history)
    #save the model
    model.save_weights("7mer-model.ckpt")

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
