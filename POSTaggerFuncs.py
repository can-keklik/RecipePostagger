import os
import string
import tempfile

import nltk
from nltk import WordNetLemmatizer

import utils

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
                            eachSent.append((direcWord, TAG, j))
            if len(eachSent) < counter:
                eachSent.append((direcWord, _, 0))
        updatedArr.append(eachSent)
    return updatedArr


def tokenize(sentence):
    removedPunctiationsData = sentence.translate(None, string.punctuation)
    # lemma = []

    titleTokens = nltk.word_tokenize(sentence)

    return titleTokens  # todo change stops to lemma and configure ingredients for lemma, change titletokens


def tokenizeText(text):
    arr = []
    sents = nltk.sent_tokenize(text)
    for i in xrange(len(sents)):
        tokenizedSentence = tokenize(sents[i])
        arr.append(tokenizedSentence)

    return arr


def posTaggSent(sent):
    return imperative_pos_tag(tokenize(sent))  # , tagset='universal')


def posTagIngre(sent):
    return nltk.pos_tag(tokenize(sent), tagset='universal')


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
                if _ == 'NOUN':
                    returnArray[i][0] = (wt, 'VERB')

    return returnArray


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
