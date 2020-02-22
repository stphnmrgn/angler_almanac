"""
Python:         2.7.10
Purpose         Aggregating freshwater fish harvest records with weather conditions
Author:         Stephen Morgan
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split


# input aggregated harvest, from iNatrualist and World Weather Online
harvest = r"C:\Users\Scripts\RandomForest_Sample_Trip.csv"

# Let's setup the data, it needs some reorganization and cleanup.
fish = pd.read_csv(harvest)
df = pd.DataFrame(fish)
df = df.drop(['dayofyear', 'angler', 'angler_id',
              'harvest_id', 'moon_phase'], axis=1)

print (df.head())
print(type(df))


"""
This is where we create some test and training datasets for the random forest regression model.
This allows us to test the model that we create on a subset of the data. This process helps 
to avoid overfitting the model on the training dataset.

Before we create the train and test data, We only want to include the attributes 
that are used in predicting harvest size. Then, using train_test_split we 
randomly assign a portion of our data as training data.
"""
# quick and dirty assinging some rows to test data
Xfish = df.iloc[:, 1:12]
yfish = df.iloc[:, 0:1]
X_train, X_test, y_train, y_test = train_test_split(Xfish, yfish, random_state=0)

# see how many observations for each dataframe
print "Number of oberservations in training data: ", len(X_train)
print "Number of oberservations in test data: ", len(X_test)
# view X training data
print(X_train)
print "Number of oberservations in training data: ", len(X_train)
# view X training data
print(X_test)
print "Number of oberservations in training data: ", len(X_test)
# view y training data
print(y_train)
print "Number of oberservations in y training data: ", len(y_train)
# view y test data
print(y_test)
print "Number of oberservations in y test data: ", len(y_test)

# create random forest regressor object
regressor = RandomForestRegressor(
    n_estimators=300, 
    random_state=0, 
    n_jobs=-1).fit(X_train, y_train)

regimport = regressor.feature_importances_

Importance = pd.DataFrame(
    data=regimport, 
    index=X_train.columns, 
    columns=['Importance'])
    
Importance = Importance.sort_values(by=['Importance'], ascending=False)[0:5]
Importance = Importance.index.values.tolist()
print "Top 5 weather variables by importance: \n", Importance

# Returns score of test and training models at predicting y variable
scoretrain = regressor.score(X_train, y_train)
scoretest = regressor.score(X_test, y_test)
print "Harvest dataset"
print "Accuracy of RF regressor on training set: {:.2f}".format(scoretrain)
print "Accuracy of RF regressor on test set: {:.2f}".format(scoretest)

# return number of features used in regressor model (X variables)
print regressor.n_features_

# Predict regression target for Xtest
y_pred = regressor.predict(X_test)
print(y_pred)

plt.scatter(y_test, y_pred)
plt.xlim([0, 15])
plt.ylim([0, 15])
plt.plot([0, 15], [0, 15])
