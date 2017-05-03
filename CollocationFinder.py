import string

import nltk.corpus
import pandas as pd
from nltk.collocations import *

import utils
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import brown



ignored_words = nltk.corpus.stopwords.words('english')
bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()
lemmatizer = WordNetLemmatizer()

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
        wholeData.extend(unionToolWords(stops))
    return wholeData


def convertTools_fromcsv():
    df = pd.read_csv("/Users/Ozgen/Desktop/RecipeGit/csv/output.csv", encoding='utf8')

    directions = df.ix[121, :].directions.encode('utf8')
    removedPunctiationsData = directions.translate(None, string.punctuation)
    titleTokens = nltk.word_tokenize(removedPunctiationsData.decode('utf-8'))
    stops = [w.lower() for w in titleTokens if w not in ignored_words and len(w) > 2]
    print unionToolWords(stops)


def unionToolWords(directionToken):
    twoWordToolList = [w.replace(" ", "_") for w in utils.tools if " " in w]
    retArr = []
    for i in xrange(len(directionToken) - 1):
        word = directionToken[i]
        secondWord = directionToken[i + 1]
        flag = False
        for tool in twoWordToolList:
            if word in tool and secondWord in tool:
                if tool not in retArr:
                    retArr.append(tool)
                    flag = True

        if word not in retArr and not flag:
            secondFlag = False
            if len(retArr) > 0:
                for w in retArr:
                    if word in w:
                        secondFlag = True
            if not secondFlag:
                retArr.append(word)

    return retArr


#convertTools_fromcsv()
#print calculateCollocation("cookie_sheet")

def giveTheMostCommonTag(tokenizedWords):
    retArr = [];
    for i in xrange(len(tokenizedWords)):
        lem = lemmatizer.lemmatize(tokenizedWords[i], 'v')
        table = nltk.FreqDist(t for w, t in brown.tagged_words() if w.lower() == lem)
        if len(table.most_common()) > 0:
            (tag, count) = table.most_common()[0]
            retArr.append(table.most_common())
    return retArr

print giveTheMostCommonTag(["cream"])