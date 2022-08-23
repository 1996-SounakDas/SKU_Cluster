# -*- coding: utf-8 -*-
"""MtechProjectFinal.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1HkPZO3aNEcG3rYBkQKW2n3joOhbd4Man

# Clustering in SKU Segmentation
This is an attempt to pipeline the model. The aim is to obtain the best algorithm based on the external performance evaluation metrics as it can be realised upon looking in the data that there is a lack of ground truth.

The script utilizes a free software machine learning library “scikit-learn” as a core
complementing it with several algorithms.
The script uses the concept of data-pipeline to consequentially perform the following procedures:
1. to impute the missing data with Multivariate Imputation
2. to standardize the data
3. to identify and trim outliers and small 'blobs' with Isolation Forest
4. to cluster the data with k-mean, BIRCH and Affinity Propagation
5. to improve the eventual clustering result via PCA

Since the ground truth is not provided, the clustering is validated only by internal evaluation, namely
by silhouette index, Calinski-Harabazs index and Davies-Bouldin '''

## Import the necessary libraries
The libraries that are being used are imported at the beginning.
"""

import pandas as pd
import numpy as np
import io
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.preprocessing import MaxAbsScaler
from itertools import cycle
from matplotlib import pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, AffinityPropagation,Birch
from sklearn import metrics
from sklearn.metrics import davies_bouldin_score

"""## Pipelining Class
This ensures that the methods are being piped into the model as well.
"""

class Pipeline:

    def __init__(self, methods):
        self.methods = methods

    def pump(self):
        for method in self.methods:
            method

"""## Data Pre-Processing
This stage has the functions that are responsible for Data imputation (using Multivariate Imputation using Chained Equation), Standardization (using MaxAbsScaler) and Outlier Identification (using Isolation Forest). The data obtained will be void of any outliers.
"""

class Processing:

    def __init__(self, data, initial_strategy = 'mean', max_features=6):
        self.data = data
        self.initial_strategy = initial_strategy
        self.max_features = max_features

    def mice(self, initial_strategy):
        self.data = pd.DataFrame(IterativeImputer(self.k)).fit_transform(self.data)

    def standardization(self):
        self.data = preprocessing.MaxAbsScaler(self.data).fit_transform(self.data)

    def outlier_removal(self,max_features):
        iso = IsolationForest(self.max_features)
        predicted = iso.fit_predict(self.data)
        index = []
        for i in range(len(predicted)):
            if predicted == -1:
                index.append(i)

        print(len(index), " outliers are found")

        self.data = np.delete(self.data,index,0)
    def get_data(self):
        return self.data

"""## Feature Reduction
This stage has the functions that are responsible for dimensionality reduction. Upon conducting variance analysis, 2 factors account for 95% of the variance associated with the features. So, the number of components are kept 2.
"""

class Reduction:

    def __init__(self, n_components=2):
        self.n_components = n_components

    def pca(self, data):
        compressor = PCA(self.n_components)
        compressor.fit(data)
        return compressor.transform(data), compressor.explained_variance_ratio_.sum()

"""## Clustering
Algorithms like K-means, BIRCH and Affinity Propagation are implemented in these functions. It is linked to the evaluation metrics and the plotter functions which will plot the distributions of the 2 components with respect to each other.
"""

class Clustering:

    def __init__(self, data):
        self.data = data

    def k_means_clustering(self, k, plot_best=True, compress=0):
        if compress != 0:
            r = Reduction(compress)
            self.data, variance = r.pca(self.data)
            print(variance)

        km = KMeans(n_clusters=k, random_state=0).fit(self.data)
        labels = km.predict(self.data)

        if plot_best is True:
            red = Reduction(n_components=2)
            to_plot, variance = red.pca(self.data)
            labels_unique = np.unique(labels)
            n_clusters_ = len(labels_unique)
            plot = Plot()
            plot.plot_clustering(to_plot, n_clusters_, labels, variance, 'K-means')

        e = Evaluation(self.data, labels)
        print(k, '-means')
        e.evaluate()

    def birch(self, k, thresh, brnc_fac, plot_best=True, compress=0):
        if compress != 0:
            r = Reduction(compress)
            self.data, variance = r.pca(self.data)
            print(variance)

        brc = Birch(n_clusters=k, threshold = thresh, branching_factor = brnc_fac, random_state=0).fit(self.data)
        labels = brc.predict(self.data)

        if plot_best is True:
            red = Reduction(n_components=2)
            to_plot, variance = red.pca(self.data)
            labels_unique = np.unique(labels)
            n_clusters_ = len(labels_unique)
            plot = Plot()
            plot.plot_clustering(to_plot, n_clusters_, labels, variance, 'BIRCH')

        e = Evaluation(self.data, labels)
        print('BIRCH')
        e.evaluate()

    def affinity(self, damp, plot_best=True, compress=0):
        if compress != 0:
            r = Reduction(compress)
            self.data, variance = r.pca(self.data)
            print(variance)

        ap = AffinityPropagation(damping = damp).fit(self.data)
        labels = ap.predict(self.data)

        if plot_best is True:
            red = Reduction(n_components=2)
            to_plot, variance = red.pca(self.data)
            labels_unique = np.unique(labels)
            n_clusters_ = len(labels_unique)
            plot = Plot()
            plot.plot_clustering(to_plot, n_clusters_, labels, variance, 'Affinity Propagation')

        e = Evaluation(self.data, labels)
        print('Affinity Propagation')
        e.evaluate()

"""## Evaluation Metrics
These are linked with each of the clustering algorithm. Here due to the absence of any sort of categorical variables or any variables indicating the "ground truth", internal evaluation metrics like Silhouette coefficient, Calinski-Harabasz Index and Davies-Bouldin Index are used to measure the effectiveness of the clustering. These metrics measure the inter- and intra-cluster distances by using different approaches.
"""

class Evaluation:

    def __init__(self, data, labels, metric='euclidean'):
        self.data = data
        self.labels = labels
        self.metric = metric

    def silhouette(self):
        return metrics.silhouette_score(self.data, self.labels, metric=self.metric)

    def calinski_harabaz(self):
        return metrics.calinski_harabaz_score(self.data, self.labels)

    def dunn_index(self):
        def normalize_to_smallest_integers(labels):
            max_v = len(set(labels))

            sorted_labels = np.sort(np.unique(labels))
            unique_labels = range(max_v)
            new_c = np.zeros(len(labels), dtype=np.int32)
            for i, clust in enumerate(sorted_labels):
                new_c[labels == clust] = unique_labels[i]
            return new_c

        def Davies_Bouldin(labels, distances):
            return metrics.davies_bouldin_score(self.data,self.labels)

    def evaluate(self):
        coeff = ['Silhouette: ', self.silhouette(), 'Calinski-Harabaz: ',
                 self.calinski_harabaz(), 'Davies Bouldin: ', self.Davies_Bouldin()]
        print(coeff)

"""## Plotter Function
These functions are used to plot the distribution of the two principal components obtained after principal component analysis. This helps to visualize the clustering that is obtained. After plotting the distributions of the plot i a scatter plot, colouring is used to denote the clusters that are obtained.
"""

class Plot:

    def plot_clustering(self, data, n_clusters_, labels, variance, name):
        plt.figure()
        plt.rc('font', size=10)
        colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
        for k, col in zip(range(len(u_label3)), colors):
                my_members = labels == k
                plt.plot(d3[my_members, 1], d3[my_members, 0], col + '.')
        plt.xlabel('Principal Component 1')
        plt.ylabel('Principal Component 2')
        plt.title('Algoritm: {} Number of clusters: {}. \n'
                  '{}% of variance is preserved after PCA'.format(name, n_clusters_, round(variance*100, 2)))
        plt.show()

"""## Uploading the File
Here, pandas dataframes are used to make the files more readable in the context of the interpreter. The initial variables are dropped as they are either categorical in nature or do not contribute any meaningful insights on data (like ID). The missing values denoted by 0.0 are replaced by the numpy character "NaN".
"""

file = pd.read_excel(io.stringIO(uploaded['initial_data.xlsx']))
data = file.parse("Sheet1")
data[['Unitprice', 'Expire date', 'Outbound number','Total outbound','Pal grossweight', 'Pal height',
      'Units per pal']] = data[['Unitprice', 'Expire date', 'Outbound number','Total outbound','Pal grossweight',
                                'Pal height', 'Units per pal']].replace(0.0, np.nan)
data = data.drop(["ID", "Tradability",  "Init status"], axis=1)
data.head()

"""It finds the number of missing values for each feature."""

data.isnull().sum()

"""Calculating the pearson's correlation amongst the features based on the data that is present."""

data.corr(method ='pearson')

"""Two features Total Outbound and Outbound number has a very strong linear correlation as obtained from the previous exercise of calculating the correlation and Evan's classification is used to obtain the relative strength of the linear correlation."""

data['Outbound Fraction'] = data['Total outbound']/data['Outbound number']
data = data.drop(['Outbound number','Total outbound'],axis = 1)
data.head()

"""Calculating the correlation amongst the features that are obtained after the previous exercise."""

data.corr(method ='pearson')

"""## Inputing the hyperparameter features
Here, the parameter values used in the algorithms are input.
"""

p = Processing(data, 6)
preprocessing_methods = [p.mice(), p.standardization(), p.outlier_removal()]
pipe1 = Pipeline(preprocessing_methods)
pipe1.pump()
c = Clustering(p.get_data())
pipe2 = Pipeline([c.k_means_clustering(8, plot_best=True, compress=2)])
pipe2.pump()