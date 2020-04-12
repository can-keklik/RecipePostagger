import os
import string
import tempfile

import nltk
from nltk import WordNetLemmatizer

import utils

import pandas as pd
import numpy as np




def readTaggedData():
    data = pd.read_csv("nyt-ingredients-snapshot-2015.csv", encoding="utf-8")
    data = data.fillna(method="ffill")
    data.tail(10)


"""functions below  are used for only crf tagging """

lemmatizer = WordNetLemmatizer()


# this function is used for tagging ingredient

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


"""old version of crf tag changer which has bugs"""


def updateDireTagsAfterCRF(dire, ingre):
    updatedArr = []
    for i in xrange(len(dire)):
        eachSent = []
        counter = 0;
        for (direcWord, _) in dire[i]:
            counter = counter + 1
            for j in xrange(len(ingre)):
                for (ingredient, TAG) in ingre[j]:
                    ingredientLemma = lemmatizer.lemmatize(ingredient)
                    if direcWord == ingredient or direcWord == ingredientLemma:
                        if len(eachSent) < counter:
                            eachSent.append((direcWord, TAG, j + 1))
            if len(eachSent) < counter:
                eachSent.append((direcWord, _, 0))
        updatedArr.append(eachSent)
    return updatedArr


def updateDireTagsAfterCRF2(dire, ingre):
    retArr = []
    for i in xrange(len(dire)):
        eachSent = []
        for j, (direWord, tag) in enumerate(dire[i]):
            for k in xrange(len(ingre)):
                for l, (ingredientWord, tag_ing) in enumerate(ingre[k]):
                    ingredientLemma = lemmatizer.lemmatize(ingredientWord)
                    if (direWord == ingredientWord or direWord == ingredientLemma) and len(eachSent) < int(j + 1):
                        eachSent.append((direWord, tag_ing, k + 1))

            if len(eachSent) < int(j + 1):
                eachSent.append((direWord, tag, 0))
        retArr.append(eachSent)
    return retArr


def tokenize(sentence):
    #removedPunctiationsData = sentence.translate(None, string.punctuation)
    # lemma = []

    titleTokens = nltk.word_tokenize(sentence)

    return titleTokens  # todo change stops to lemma and configure ingredients for lemma, change titletokens


def tokenizeText(text):
    arr = []
    sents = nltk.sent_tokenize(text)
    for i in xrange(len(sents)):
        tokenizedSentence = tokenize(sents[i])
        arr.append(tokenizedSentence)
    arr = updateTextWithSemicolon(arr)
    return arr


def posTaggSent(sent):
    sent = str(sent).replace("I would ","")
    res = imperative_pos_tag(tokenize(sent))  # , tagset='universal')
    (wt, _)= res[0]
    if _ == 'NOUN':
        res[0] = (wt, 'VERB')
    return res

def posTagIngre(sent):
    return nltk.pos_tag(tokenize(sent), tagset='universal')


def posTaggText(text):
    returnArray = []
    arr = tokenizeText(text)
    for i in xrange(len(arr)):
        returnArray.append(imperative_pos_tag(arr[i]))  # , tagset='universal'))
    for i in xrange(len(returnArray)):
        for (wt, _) in returnArray[i]:
            if returnArray[i][0] == (wt, _):
                if _ == 'NOUN':
                    returnArray[i][0] = (wt, 'VERB')

    return returnArray


def updateTextWithSemicolon(textArr):
    retArr = []
    for eachSent in textArr:
        tmp = [w for w in eachSent if ";" in w]
        if len(tmp) > 0:
            tmpSent = splitSentenceWithSemiColon(eachSent)
            if len(tmpSent) > 0:
                for s in tmpSent:
                    retArr.append(s)
        else:
            retArr.append(eachSent)
    return retArr


def splitSentenceWithSemiColon(sentence):
    retArr = []
    tmp = []
    for word in sentence:
        if ";" not in word:
            tmp.append(word)
        else:
            retArr.append(tmp)
            tmp = []
    if len(tmp) > 0:
        retArr.append(tmp)
    return retArr


def imperative_pos_tag(sent):
    # todo mislea dataset "I would" is used rather than   "He"
    return nltk.pos_tag(['I would'] + sent, tagset='universal')[1:]


def configureIngredientforCRF(ingredients):
    for i in xrange(len(ingredients)):
        tokenizedData = utils.tokenize(ingredients[i])
        # cli.Cli.addPrefixes([(t, self.matchUp(t, row)) for t in tokenizedData])


def getNameEntityInIngre(data):
    returnArr = []
    for i in xrange(len(data)):
        arr = [wt for (wt, _) in data[i] if 'NAME' in _]
        if (len(arr) > 0):
            returnArr.extend(arr)
    return returnArr


# print(parse_ingredientForCRF(["3/4 pound cooked chicken breast meat very finely chopped"]))
# print(parse_ingredientForCRF(["2 tomatoes sliced"]))
# print(parse_ingredientForCRF(["1/4 cup chopped pecans"]))
