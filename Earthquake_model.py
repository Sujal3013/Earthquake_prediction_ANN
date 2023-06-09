# -*- coding: utf-8 -*-
"""Untitled3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vQp98wIl3laFNH1oObWARFh957jDjXgs
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data=pd.read_csv('earthquake_data.csv')
data=data[['Date','Time','Latitude','Longitude','Depth','Magnitude']]

"""Scaling date and time"""

import datetime
import time

timestamp=[]
for d,t in zip(data['Date'],data['Time']):
  try:
    ts=datetime.datetime.strptime(d+' '+t, '%m/%d/%Y %H:%M:%S')
    timestamp.append(time.mktime(ts.timetuple()))
  except ValueError:
    #print(ValueError)
    timestamp.append('ValueError')

timeStamp=pd.Series(timestamp)
data['TimeStamp']=timeStamp.values
data.head()

final_data=data.drop(['Date','Time'],axis=1)
final_data=final_data[final_data.TimeStamp!='ValueError']
final_data.head()


""" Magnitude Classes
Disastrous: M > =8
Major: 7 < =M < 7.9
Strong: 6 < = M < 6.9
Moderate: 5.5 < =M < 5.9
"""

data.loc[data['Magnitude'] >=8, 'Class'] = 'Disastrous'
data.loc[ (data['Magnitude'] >= 7) & (data['Magnitude'] < 7.9), 'Class'] = 'Major'
data.loc[ (data['Magnitude'] >= 6) & (data['Magnitude'] < 6.9), 'Class'] = 'Strong'
data.loc[ (data['Magnitude'] >= 5.5) & (data['Magnitude'] < 5.9), 'Class'] = 'Moderate'

"""# Splitting data and Creating the Model"""

X = final_data[['TimeStamp', 'Latitude', 'Longitude']]
y = final_data[['Magnitude', 'Depth']]

from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,random_state=0)

from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import GridSearchCV
from keras.models import Sequential
from keras.layers import Dense,Activation,Embedding,Flatten,LeakyReLU,BatchNormalization,Dropout
from keras.activations import relu, sigmoid
from keras.layers import LeakyReLU

# 3 dense layers, 16, 16, 2 nodes each

def create_model(neurons, activation, optimizer, loss):
    model = Sequential()
    model.add(Dense(neurons, activation=activation, input_shape=(3,)))
    model.add(Dense(neurons, activation=activation))
    model.add(Dense(2, activation='softmax'))
    
    model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])
    
    return model

from keras.wrappers.scikit_learn import KerasClassifier

model = KerasClassifier(build_fn=create_model, verbose=0)
param_grid = {
    "neurons": [16], 
    "batch_size": [10, 20], 
    "epochs": [10],
    "activation": ['sigmoid', 'relu'],
    "optimizer": ['SGD', 'Adadelta'],
    "loss": ['squared_hinge']
}

'''Datatype correction in training and testing sets'''

X_train = np.asarray(X_train).astype(np.float32)
y_train = np.asarray(y_train).astype(np.float32)
X_test = np.asarray(X_test).astype(np.float32)
y_test = np.asarray(y_test).astype(np.float32)

grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=-1)
grid_result = grid.fit(X_train, y_train)

"""Training on best hyperparameters"""

model= Sequential()

model.add(Dense(16,activation='sigmoid',input_shape=(3,)))
model.add(Dense(16,activation='sigmoid'))
model.add(Dense(2,activation='softmax'))

model.compile(optimizer='Adadelta',loss='squared_hinge',metrics=['accuracy'])
model.fit(X_train,y_train,batch_size=20,epochs=10,verbose=1,validation_data=(X_test,y_test))

[test_loss,test_acc]=model.evaluate(X_test,y_test)
