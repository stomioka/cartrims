# -*- coding: utf-8 -*-
"""
Created on Sun Sep 22 17:27:04 2019

@author: Sam
"""

import pandas as pd
import numpy as np
df=pd.read_csv("G:\GoogleDrive\GitHub\cars\carsReviews.csv")

def max_find(column):
    df['l']=df.apply(lambda x: len(x[column]) if x[column] is not np.nan else 0, axis=1)
    return np.array(df['l']).max()

for i in df.columns:
    print(max_find(i))

df.columns

max_find('author') #50
max_find('comfort') #num
max_find('date') #15
max_find('exteriorStyling') #num
max_find('helpful') #num
max_find('interior') #num
max_find('location') #50
max_find('make') #13
max_find('model') #31
max_find('modelYear')  #num
max_find('new') #4
max_find('outOf') #num
max_find('performance') #num
max_find('rating') #num
max_find('recommend') #8
max_find('reliability') #num
max_find('reviewBody') #10000
max_find('title') #50
max_find('url') #150
max_find('use') #40
max_find('value') #num

max_find('recommend') #num
measurer = np.vectorize(len)
res1 = measurer(df.values.astype(str)).max(axis=0)