'''
Title:          ranges.py
Python:         2.7.10
Purpose         Finding the value ranges for each weather variable
Author:         Stephen Morgan
Date:           03/06/2018
'''

# import really important modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# import the big daddy module
from sklearn.ensemble import RandomForestRegressor


harvest = r"C:\Users\steph\Documents\Python\Projects\Silas\Scripts\RandomForest_training.csv"


'''
Let's setup the data, it needs some reorganization and cleanup. 
We'll use Pandas to work with our csv harvest data.
'''
# set the harvest data to the object fish
fish = pd.read_csv(harvest)
# create dataframe with weather variables
df = pd.DataFrame(fish)
# view top 5 rows
df.head()
# drop fields from dataframe that we do not need
df = df.drop(['common_name', 'UTC', 'date', 'year', 'latitude',
              'longitude', 'angler', 'angler_id', 'harvest_id'], axis = 1)

'''
Add a label, aka column, indicating whether our angler was successful. 
Right now they're all successful because our harvest data is of
sucessfull anglers. Later that will change when we need some failures. 
When that time comes, use the second line here.
'''
#df['success'] = 'True' <<--add back if failure isnt needed
df['success'] = np.random.randint(0, 2, len(df)) <= 0.75
# create test and train dataframes
success, failure = df[df['is_train'] == True], df[df['is_train'] == False]
# see how many observations for each dataframe
print "Number of oberservations in success data: ", len(train)
print "Number of oberservations in failure data: ", len(test)

'''
Figure out the range of values for each weather variable so we can 
later create a subsample of harvest data with random values populated 
in each weather variable. The random values need to be within the normal
range of the real data. We wil use this subsample as the training dataset
for the random forest regression module.
'''
# create variables to hold the min and max values for specific columns
# use iloc to select by label, aka header
var_max = df.iloc[:, 4:15].max(axis = 0)
var_min = df.iloc[:, 4:15].min(axis = 0)
# view min and max values
var_max
var_min
# create dataframes from max and min values
dfmax = pd.DataFrame(var_max)
dfmin = pd.DataFrame(var_min)

# create list of min and max values
d = ([var_min, var_max])
# create dataframe with the max and min values
df2 = pd.DataFrame(d, index = ['Minimum', 'Maximum'])
# view the dataframe of min and max values
df2.head()

# get the difference between the max & min of the 1st column
df2.iloc[1, 0] - df2.iloc[0, 0]
# get the difference between all max & min values
df2.iloc[1, ] - df2.iloc[0, ]

# create dataframe with max/min columns instead
#nindex = dfmin.columns[:11]
df3 = pd.DataFrame(dfmin)
# add Min & Max labels to dataframe, populate with values from dfmin/dfmax 1st column
df3['Minimum'] = dfmin[0]
df3['Maximum'] = dfmax[0]
# drop "0" label from database
df3 = df3.drop(0, 1)
# view the dataframe of min and max values
df3
