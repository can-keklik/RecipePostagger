from operator import itemgetter

import gensim
import numpy as np
from scipy import spatial

model = gensim.models.Word2Vec.load('SmallerFile', mmap='r')
type(model.syn0)
model.syn0.shape


def makeFeatureVec(words, model, num_features):
    # Function to average all of the word vectors in a given
    # paragraph
    #
    # Pre-initialize an empty numpy array (for speed)
    featureVec = np.zeros((num_features,), dtype="float32")
    #
    nwords = 0.
    #
    # Index2word is a list that contains the names of the words in
    # the model's vocabulary. Convert it to a set, for speed
    index2word_set = set(model.index2word)
    #
    # Loop over each word in the review and, if it is in the model's
    # vocaublary, add its feature vector to the total
    for word in words:
        if word in index2word_set:
            nwords = nwords + 1.
            featureVec = np.add(featureVec, model[word])
    #
    # Divide the result by the number of words to get the average
    featureVec = np.divide(featureVec, nwords)
    return featureVec


def createCosSim(verbArray, wholeVerbs):
    cosSimArr = []
    for vr in verbArray:
        arry = []
        secondVerbArr = [v for v in wholeVerbs if v != vr]
        vrArr = str(vr).split(" ")
        if len(vrArr) > 1:
            verb1 = makeFeatureVec(vrArr, model=model, num_features=300)
        else:
            verb1 = model[vr]

        for v_s in secondVerbArr:
            vsArr = str(v_s).split(" ")
            if len(vsArr) > 1:
                verb2 = makeFeatureVec(vsArr, model=model, num_features=300)
            else:
                verb2 = model[v_s]
            try:
                cosSim = 1 - spatial.distance.cosine(verb1, verb2)
                a = [vr, v_s, cosSim]
                arry.append(a)
            except KeyError:
                pass
        if len(arry) > 0:
            maxVal = max(arry, key=itemgetter(2))[2]
            minVal = min(arry, key=itemgetter(2))[2]

        for i in xrange(len(arry)):
            data = arry[i]
            p = (data[2] - minVal) / (maxVal - minVal);
            if p > 0.80:  # todo check min max value
                if (data[0], data[1], p) not in cosSimArr and (data[1], data[0], p) not in cosSimArr:
                    cosSimArr.append((data[0], data[1], p))
    return cosSimArr
