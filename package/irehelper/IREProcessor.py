from operator import index
import numpy as np
import pandas as pd
import math as m
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


class IREProcessor:
    def __init__(self, pcomment):
        self.pcomment = pcomment

    def createVectorizerImplementation(self, corpus):
        vectorizer = TfidfVectorizer(use_idf=True)
        # idf = vectorizer.idf_
        # features = vectorizer.get_feature_names()
        # print(dict(zip(features, idf)))
        return vectorizer.fit_transform(corpus)

    # Create a term by document matrix
    def createTermDocumentMatrix(self, corpus):
        # Create a set of terms
        features = set()
        tokenList = []
        for doc in corpus:
            tokens = doc.split()
            tokenList.append(tokens)
            features = features.union(set(tokens))

        # Create a term frequency dictionary for each token list
        freqList = []
        for tokens in tokenList:
            freq = dict.fromkeys(features, 0)
            for token in tokens:
                freq[token] += 1
            freqList.append(freq)

        return freqList

    # Apply TNC weigthing on the t-d matrix
    def applyTNCWeighting(self, freqList):
        tncList = []
        for i in range(len(freqList)):
            type(freqList[i])
            tncList.append(self.computeLocalWeight(
                freqList[i], freqList))

        globalWeights = self.computeGlobalWeights(freqList)
        globalWeights = list(globalWeights.items())

        tncList, _ = self.convertDictToMatrix(tncList)
        for i in range(len(globalWeights)):
            tncList[:, i] = tncList[:, i] * globalWeights[i][1]

        return tncList

    # Compute the local weights for a a term in a document
    def computeLocalWeight(self, freq, freqList):
        weightedDict = {}
        lenDoc = sum(freq.values())

        # Local Term frequency weighting and Global Normal weighting
        # (fij / total terms) * (1 / sqrt(sumj((fij)^2)))
        for token, count in freq.items():
            weightedDict[token] = (count / lenDoc)

        return weightedDict

    # Compute global weights for the terms
    def computeGlobalWeights(self, freqList):
        globalWeights = dict.fromkeys(freqList[0].keys(), 0)
        matrix, features = self.convertDictToMatrix(freqList)
        N = len(freqList)

        for key, _ in globalWeights.items():
            featIndex = features.index(key)
            col = matrix[:, featIndex]
            col = list(filter(lambda x: x != 0, col))
            globalWeights[key] = m.log2((N + 1) / (float(len(col)) + 1) + 1)

        return globalWeights

    # Decompose the td-matrix using SVD
    def calculateSVD(self, matrix):
        U, sigma, Vt = np.linalg.svd(matrix)
        sigma = np.diag(sigma)
        return U, sigma, Vt

    # Reduce dimension of the matrix
    def reduceDimensions(self, k, matrix):
        reducedMatrix = matrix[:, :k]
        return reducedMatrix

    # Create a matrix from list of dictionary
    def convertDictToMatrix(self, freqList):
        features = []

        # Extract features
        for key, _ in freqList[0].items():
            features.append(key)

        matrix = np.empty((0, len(features)))
        for freq in freqList:
            dictList = [value for _, value in freq.items()]
            matrix = np.vstack([matrix, dictList])

        return matrix, features

    # Calculate the magnitude of a vector(list)
    def calculateMagnitude(self, vector):
        return m.sqrt(sum(list(map(lambda x: x*x, vector))))

    # Calculate the similarity
    def calculateSimilarity(self, matrix):
        matrix = matrix.transpose()

        # Calculate magniture for each document
        for i in range(matrix.shape[1]):
            magnitude = self.calculateMagnitude(matrix[:, i])
            matrix[:, i] = matrix[:, i] / magnitude

        U, sigma, Vt = self.calculateSVD(matrix)

        # Reducing dimensions to the shape of sigma
        # Here, k == r, so the value is the same as cosine similarity
        U = self.reduceDimensions(sigma.shape[0], U)
        V = self.reduceDimensions(sigma.shape[0], Vt.transpose())
        val = V.dot(sigma)
        result = val.dot(val.transpose())
        print(result)
