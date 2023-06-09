# -*- coding: utf-8 -*-
"""Copy of Major_Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kTGjhmxjKxtgc66jZVfWUUMvZshZR4FN
"""

import numpy as np 
import pandas as pd 
import json # neccessary for performing operations on json file
import os # neccessary for file related operations
import re # neccessary for data preprocessing

with open('/content/intents.json', 'r') as f:
    data = json.load(f) # data is in the form of json

df = pd.DataFrame(data['intents'])
df
#converting the given data into a dataframe format without any modifications

dic = {"tag":[], "patterns":[], "responses":[]}
for i in range(len(df)):
    ptrns = df[df.index == i]['patterns'].values[0]
    rspns = df[df.index == i]['responses'].values[0]
    tag = df[df.index == i]['tag'].values[0]
    for j in range(len(ptrns)):
        dic['tag'].append(tag)
        dic['patterns'].append(ptrns[j])
        dic['responses'].append(rspns)
        
df = pd.DataFrame.from_dict(dic)
df

df['tag'].unique()
#There are 80 tags

from tensorflow.keras.preprocessing.text import Tokenizer
tokenizer = Tokenizer(lower=True, split=' ') # Converting the data into tokens by tokenization (Data Preprocessing)
tokenizer.fit_on_texts(df['patterns']) # used further
tokenizer.get_config()# inorder to see

from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder

ptrn2seq = tokenizer.texts_to_sequences(df['patterns']) #transforms the text into sequence of integers
# here we are using these methods called fit_to_text and texts_to_sequences of tokenizer and not alone this tokenizer as we not only wanted  to tokenize the sentences but also
# vectorize the tokenized words..
X = pad_sequences(ptrn2seq, padding='post')#pad_sequences converts the given array into a given number of dimensions, if not provided the dimensions,, then it will take the longer
# size by default
# X
# # ptrn2seq
print('X shape = ', X.shape)

lbl_enc = LabelEncoder()
y = lbl_enc.fit_transform(df['tag'])	
y
# Fit label encoder and return encoded labels.
print('y shape = ', y.shape)
print('num of classes = ', len(np.unique(y)))

from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder

ptrn2seq = tokenizer.texts_to_sequences(df['patterns'])

ptrn2seq

X = pad_sequences(ptrn2seq, padding='post')

X

X.shape

vacab_size = len(tokenizer.word_index)
print('number of unique words = ', vacab_size)

import tensorflow
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Embedding, LSTM, LayerNormalization, Dense, Dropout
from tensorflow.keras.utils import plot_model

model = Sequential()
model.add(Input(shape=(X.shape[1])))
model.add(Embedding(input_dim=vacab_size+1, output_dim=100, mask_zero=True))
model.add(LSTM(32, return_sequences=True))
model.add(LayerNormalization())
model.add(LSTM(32, return_sequences=True))
model.add(LayerNormalization())
model.add(LSTM(32))
model.add(LayerNormalization())
model.add(Dense(128, activation="relu"))
model.add(LayerNormalization())
model.add(Dropout(0.2))
model.add(Dense(128, activation="relu"))
model.add(LayerNormalization())
model.add(Dropout(0.2))
model.add(Dense(len(np.unique(y)), activation="softmax"))
model.compile(optimizer='adam', loss="sparse_categorical_crossentropy", metrics=['accuracy'])

model.summary()
plot_model(model, show_shapes=True)

model_history = model.fit(x=X,
                          y=y,
                          batch_size=10,
                          callbacks=[tensorflow.keras.callbacks.EarlyStopping(monitor='accuracy', patience=3)],
                          epochs=50)

import re
import random

def generate_answer(pattern): 
    text = []
    txt = re.sub('[^a-zA-Z\']', ' ', pattern)
    txt = txt.lower()
    txt = txt.split()
    txt = " ".join(txt)
    text.append(txt)
        
    x_test = tokenizer.texts_to_sequences(text)
    x_test = np.array(x_test).squeeze()
    x_test = pad_sequences([x_test], padding='post', maxlen=X.shape[1])
    y_pred = model.predict(x_test)
    y_pred = y_pred.argmax()
    tag = lbl_enc.inverse_transform([y_pred])[0]
    responses = df[df['tag'] == tag]['responses'].values[0]

    print("you: {}".format(pattern))
    print("model: {}".format(random.choice(responses)))

generate_answer('Hi! how are you')

generate_answer('WEll I a feeling sad')

generate_answer('I want to commit suicide')

