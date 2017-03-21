from __future__ import print_function

import pandas as pd

from Models import Action
from Models import Ingredient
from Models import Tool
from Models import Recipe
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
import os, shutil
import sys
import string
import cli
import utils

import tempfile
import gensim
import re, math
import numpy as np
from scipy import spatial

import UtilsIO

from nltk.corpus import wordnet as wn
from nltk.corpus import brown


# todo open comment to run vord2vec
# initialize the model
# model = gensim.models.Word2Vec.load('SmallerFile', mmap='r')
# type(model.syn0)
# model.syn0.shape


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


def makeFeatureVectorsForDire(dire):
    retArr = []
    for i in xrange(len(dire)):
        retArr.append([makeFeatureVec(dire[i], model, 300)])
    return retArr


def updateDireTagsAfterCRF(dire, ingre):
    updatedArr = []
    for i in xrange(len(dire)):
        eachSent = []
        counter = 0;
        for (direcWord, _) in dire[i]:
            counter = counter + 1
            for j in xrange(len(ingre)):
                for (ingredient, TAG) in ingre[j]:
                    if direcWord == ingredient:
                        if len(eachSent) < counter:
                            eachSent.append((direcWord, TAG))
            if len(eachSent) < counter:
                eachSent.append((direcWord, _))

        updatedArr.append(eachSent)
    return updatedArr


# nltk.download()
lemmatizer = WordNetLemmatizer()
stopwords = nltk.corpus.stopwords.words('english')


def tokenize(sentence):
    removedPunctiationsData = sentence.translate(string.punctuation).lower()
    # lemma = []
    try:
        titleTokens = nltk.word_tokenize(removedPunctiationsData)
        stops = [w for w in titleTokens if w not in stopwords]
        lemma = [lemmatizer.lemmatize(w) for w in stops]
        for w in xrange(len(stops)):
            lem = lemmatizer.lemmatize(stops[w], 'v')
            lemma.append(lem)
    except:
        titleTokens = nltk.word_tokenize(removedPunctiationsData.decode('utf-8'))
        stops = [w for w in titleTokens if w not in stopwords]
        lemma = [lemmatizer.lemmatize(w, 'v') for w in stops]
        for w in xrange(len(stops)):
            lem = lemmatizer.lemmatize(stops[w], 'v')
            lemma.append(lem)
    return stops  # todo change stops to lemma and configure ingredients for lemma


def tokenizeText(text):
    arr = []
    sents = nltk.sent_tokenize(text)
    for i in xrange(len(sents)):
        tokenizedSentence = tokenize(sents[i])
        arr.append(tokenizedSentence)

    return arr


def posTaggSent(sent):
    return imperative_pos_tag(tokenize(sent))  # , tagset='universal')


def posTaggText(text):
    returnArray = []
    arr = tokenizeText(text)
    for i in xrange(len(arr)):
        # if (i == 0):
        #    returnArray.append()
        returnArray.append(imperative_pos_tag(arr[i]))  # , tagset='universal'))
    for i in xrange(len(returnArray)):
        for (wt, _) in returnArray[i]:
            if returnArray[i][0] == (wt, _):
                if _ == 'NN':
                    returnArray[i][0] = (wt, 'VB')

    return returnArray


def imperative_pos_tag(sent):
    return nltk.pos_tag(['He'] + sent, tagset='universal')[1:]


def configureIngredientforCRF(ingredients):
    for i in xrange(len(ingredients)):
        tokenizedData = utils.tokenize(ingredients[i])
        # cli.Cli.addPrefixes([(t, self.matchUp(t, row)) for t in tokenizedData])


def parse_ingredientForCRF(ingredients):
    returnArr = []
    eachIngre = []
    _, tmpFile = tempfile.mkstemp()
    _, tmpFile2 = tempfile.mkstemp()
    with open(tmpFile, 'w') as outfile:
        outfile.write(utils.export_data(ingredients))

    tmpFilePath = "./tmp/model_file"
    modelFilename = os.path.join(os.path.dirname(__file__), tmpFilePath)
    aa = "crf_test   -m %s %s " % (modelFilename, tmpFile)
    bb = " > %s " % (tmpFile2)
    cc = " || exit 1 "
    fullCommand = aa + bb + cc
    os.system(fullCommand)
    os.system("rm %s" % tmpFile)
    f = open(tmpFile2)
    parsedData = f.read()
    os.system("rm %s" % tmpFile)
    os.system("rm %s" % tmpFile2)
    data = parsedData.split('\n')

    for sen in xrange(len(data)):
        words = data[sen].split('\t')
        name = words[0]
        name = name.translate(None, string.punctuation).lower()
        val = words[len(words) - 1]
        val2 = val.split('-')

        if val2[len(val2) - 1] != '' and name != '':
            obj = (name, val2[len(val2) - 1])
            eachIngre.append(obj)
        else:
            if len(eachIngre) > 0:
                returnArr.append(eachIngre)
            eachIngre = []

    return returnArr


def getNameEntityInIngre(data):
    returnArr = []
    for i in xrange(len(data)):
        arr = [wt for (wt, _) in data[i] if 'NAME' in _]
        if (len(arr) > 0):
            returnArr.extend(arr)
    return returnArr


def getCosineSimilarityIngreAndDire(dire, ingre, direVec):
    retArr = []
    for i in xrange(len(ingre)):
        ingreVec = model[ingre[i]]
        for j in xrange(len(direVec)):
            cosSim = 1 - spatial.distance.cosine(ingreVec, direVec[j])
            a = [ingre[i], dire[j], cosSim]
            retArr.append(a)
    return retArr


def giveTheMostCommonTag(tokenizedWords):
    retArr = [];
    for i in xrange(len(tokenizedWords)):
        lem = lemmatizer.lemmatize(tokenizedWords[i], 'v')
        table = nltk.FreqDist(t for w, t in brown.tagged_words() if w.lower() == lem)
        if len(table.most_common()) > 0:
            (tag, count) = table.most_common()[0]
            if (tag == 'VB'):
                retArr.append((tokenizedWords[i], tag))
    return retArr


def updateVerbTagIfVerbIsEmpty(sentence, taggedWord):
    if len(taggedWord) == 0:
        return sentence

    (word, newTag) = taggedWord[0]
    arr = []
    for (wt, _) in sentence:
        if (wt == word):
            tag = u'VERB'
            arr.append((wt, tag))
        else:
            arr.append((wt, _))
    return arr




    # TODO: we get postagged data array = arr and we will fill actions , ingredients and tool list


def readData():
    df = pd.read_csv("/Users/Ozgen/Desktop/RecipeGit/csv/output.csv", encoding='utf8')
    # names=["index", "title", "ingredients", "directions"])

    ingredients = df.ix[1, :].ingredients
    directions = df.ix[1, :].directions
    print(directions)
    arr = posTaggText(directions)
    ingre = [posTaggSent(w) for w in ingredients]
    dire = tokenizeText(directions)
    ingreWithNewTAG = parse_ingredientForCRF(ingredients)
    # parsData = getNameEntityInIngre(ingreWithNewTAG)
    direWithNewTAG = updateDireTagsAfterCRF(arr, ingreWithNewTAG)

    print("----------------------")
    #  print(getCosineSimilarityIngreAndDire(dire, parsData, makeFeatureVectorsForDire(dire)))
    print()
    print(ingreWithNewTAG)
    print(direWithNewTAG)
    print(arr)

    print("----------------------")

    for i in xrange(len(direWithNewTAG)):
        a = [wt for (wt, _) in direWithNewTAG[i] if 'VERB' == _]
        if (len(a) == 0):
            direWithNewTAG[i] = updateVerbTagIfVerbIsEmpty(direWithNewTAG[i], giveTheMostCommonTag(
                [wt for (wt, _) in direWithNewTAG[i]]))
        print("actions")
        print([wt for (wt, _) in direWithNewTAG[i] if 'VERB' == _])
        print("nouns")
        print([wt for (wt, _) in direWithNewTAG[i] if 'NOUN' == _])
        print("ingredients")
        print([wt for (wt, _) in direWithNewTAG[i] if 'NAME' == _])

        print("units")
        print([wt for (wt, _) in direWithNewTAG[i] if 'UNIT' == _])

        print("comments")
        print([wt for (wt, _) in direWithNewTAG[i] if 'COMMENT' == _])

        print("quantity")
        print([wt for (wt, _) in direWithNewTAG[i] if 'QTY' == _])

        print("----------------------")


readData()










# cli.Cli(20000, 0).run();

# print lemmatizer.lemmatize('reserving', 'v')
# print wn.synsets('discard')  # .root_hypernyms()


# MODEL SAVED INTO SMALLERFILE & NEXT LOAD FROM IT
# GIVE RESULT SER3!
# print(model['water'])
