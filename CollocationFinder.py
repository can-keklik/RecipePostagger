import string

import nltk.corpus
import pandas as pd
from nltk.collocations import *

ignored_words = nltk.corpus.stopwords.words('english')
bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()

wholeData = [];


def calculateCollocation(word):
    retArr = []
    global wholeData
    if len(wholeData) == 0:
        wholeData = readWholeDirections()
    # tokens = readWholeDirections()
    finder = BigramCollocationFinder.from_words(wholeData)
    scored = finder.score_ngrams(bigram_measures.raw_freq)
    sortedScored = sorted(bigram for bigram, score in scored)
    nbests = finder.nbest(bigram_measures.likelihood_ratio, 100000)
    for w1, w2 in nbests:
        if w1 == word and w2 not in retArr:
            retArr.append(w2)
        elif w2 == word and w1 not in retArr:
            retArr.append(w1)
        if len(retArr) > 50:
            break

    return retArr


def readWholeDirections():
    df = pd.read_csv("/Users/Ozgen/Desktop/RecipeGit/csv/output.csv", encoding='utf8')
    for i in xrange(1, 10426):
        directions = df.ix[i, :].directions.encode('utf8')
        removedPunctiationsData = directions.translate(None, string.punctuation)
        titleTokens = nltk.word_tokenize(removedPunctiationsData.decode('utf-8'))
        stops = [w.lower() for w in titleTokens if w not in ignored_words and len(w) > 2]
        wholeData.extend(stops)
    return wholeData


print calculateCollocation("pot")
