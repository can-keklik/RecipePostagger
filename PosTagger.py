from __future__ import print_function

import os
import string
import tempfile
from operator import itemgetter

import gensim
import nltk
import numpy as np
import pandas as pd
from nltk.corpus import brown
from nltk.stem.wordnet import WordNetLemmatizer
from scipy import spatial

import GraphGenerator
import UtilsIO
import utils
import CollocationFinder

# todo open comment to run vord2vec
# initialize the model

model = gensim.models.Word2Vec.load('SmallerFile', mmap='r')
type(model.syn0)
model.syn0.shape

# nltk.download()
lemmatizer = WordNetLemmatizer()
stopwords = nltk.corpus.stopwords.words('english')


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
                    ingredientLemma = lemmatizer.lemmatize(ingredient)
                    if direcWord == ingredient or direcWord == ingredientLemma:
                        if len(eachSent) < counter:
                            eachSent.append((direcWord, TAG))
            if len(eachSent) < counter:
                eachSent.append((direcWord, _))  # todo oven pan cup to update tool

        updatedArr.append(eachSent)
    return updatedArr


def tokenize(sentence):
    removedPunctiationsData = sentence.translate(None, string.punctuation)
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
    return stops  # todo change stops to lemma and configure ingredients for lemma, change titletokens


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
    #todo mislea dataset "I would" is used rather than   "He"
    return nltk.pos_tag(['I would'] + sent, tagset='universal')[1:]


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


# todo this function needs to refactor, not work properly
def getCosineSimilarityIngreAndDire(dire, ingre, direVec):
    retarr = []
    for j in xrange(len(direVec)):
        retarr.append((createCosSim(dire[j], ingre, direVec[j]), dire[j]))
    return retarr


def checkDireIfIngredientHasNot(direSent, ingre):
    isTrue = True
    for i in xrange(len(direSent)):
        for j in xrange(len(ingre)):
            if direSent[i] == ingre[j]:
                isTrue = False
    return isTrue


def createCosSim(direSent, ingre, direVec):
    arry = []
    if (checkDireIfIngredientHasNot(direSent, ingre)):
        for j in xrange(len(ingre)):
            try:
                ingreVec = model[ingre[j]]
                cosSim = 1 - spatial.distance.cosine(ingreVec, direVec)
                a = [ingre[j], direSent, cosSim]
                arry.append(a)
            except KeyError:
                pass
    retArr = []
    if len(arry) > 0:
        maxVal = max(arry, key=itemgetter(2))[2]
        minVal = min(arry, key=itemgetter(2))[2]

    for i in xrange(len(arry)):
        data = arry[i]
        p = (data[2] - minVal) / (maxVal - minVal);
        if p > 0.65:  # todo check min max value
            retArr.append((data[0]))

    return retArr


def giveTheMostCommonTag(tokenizedWords):
    retArr = [];
    for i in xrange(len(tokenizedWords)):
        (word, Tag) = tokenizedWords[i]
        if (i == 0 and Tag == u'VERB'):
            retArr.append((word, Tag))
        lem = lemmatizer.lemmatize(word, 'v')

        table = nltk.FreqDist(t for w, t in brown.tagged_words() if w.lower() == lem.lower())
        if len(table.most_common()) > 0:
            (tag, count) = table.most_common()[0]
            if (tag == 'VB'):
                if (word, tag) not in retArr:
                    retArr.append((word, tag))
    return retArr


def updateVerbTagIfVerbIsEmpty(sentence, taggedWord):
    if len(taggedWord) == 0:
        return sentence

    # (word, newTag) = taggedWord[0]
    arr = []
    tag = u'VERB'
    commentTag = 'COMMENT'
    for (wt, _) in sentence:
        for (word, newTag) in taggedWord:
            if (wt == word):
                if (wt, tag) not in arr and _ != commentTag:
                    arr.append((wt, tag))
            elif _ == tag:
                pass
            else:
                if (wt, _) not in arr:
                    arr.append((wt, _))
    return arr


def isTool(words):
    arr = []
    if (len(words) > 0):
        for i in xrange(len(words)):
            lemma = lemmatizer.lemmatize(word=words[i])
            arr.append(lemma)

    sentence = " ".join(arr)

    return utils.checkToolList(sentence)


# TODO: we get postagged data array = arr and we will fill actions , ingredients and tool list


def updateForTools(direSent, toolList):
    returnArr = []

    if len(toolList) > 0:
        for (direW, TAG) in direSent:
            lemma = lemmatizer.lemmatize(direW)
            for w in toolList:
                if lemma in w:
                    if (w, "TOOL") not in returnArr:
                        returnArr.append((w, "TOOL"))
                else:
                    returnArr.append((direW, TAG))
        return returnArr
    else:
        return direSent


def getNameEntityInIngres(taggedRecipe):
    returnArr = []
    for i in xrange(len(taggedRecipe)):
        arr = [wt for (wt, _) in taggedRecipe[i] if 'NAME' in _]
        if (len(arr) > 0):
            newW = " ".join(arr)
            returnArr.append(newW)
    return returnArr


def getNameEntityInIng(taggedRecipe):
    returnArr = []
    for i in xrange(len(taggedRecipe)):
        arr = [wt for (wt, _) in taggedRecipe[i] if 'NAME' in _]
        if (len(arr) > 0):
            newW = " ".join(arr)
            returnArr.append(newW)
    return returnArr


def getSpecificIngredient(word, taggedRecipe):
    ingList = getNameEntityInIng(taggedRecipe)
    retIngre = ""
    for w in ingList:
        if word in w:
            retIngre = w

    return retIngre


def optimizeTagWithCollocation(param):
    toolList = [wt.replace(" ", "_") for (wt, _) in param if 'TOOL' == _]
    actionList = [wt for (wt, _) in param if 'VERB' == _]
    toRemove = []
    retArr = []
    if len(toolList) > 0:
        for tool in toolList:
            collList = CollocationFinder.calculateCollocation(tool)
            if len(collList) > 0 and len(actionList) > 1:
                for colW in collList:
                    for verb in actionList:
                        if verb == colW:
                            if (tool, verb) not in toRemove:
                                toRemove.append((tool, verb))

        if len(toRemove) > 0:
            print('toremove ', toRemove)
            for (w, T) in param:
                for t, rmovalWord in toRemove:
                    if (w != rmovalWord) and (w, T) not in retArr:
                        retArr.append((w, T))

        return retArr
    else:
        return param


def readData(index, df=None):
    if df == None:
        df = pd.read_csv("./csv/allrecipes.csv", encoding='utf8')
    # names=["index", "title", "ingredients", "directions"])

    ingredients = df.ix[index, :].ingredients.encode('utf8')
    ingredients = (utils.convertArrayToPureStr(ingredients))
    directions = df.ix[index, :].directions.encode('utf8')
    ingre = [posTagIngre(w) for w in ingredients]
    arr = posTaggText(directions)
    dire = tokenizeText(directions)
    ingreWithNewTAG = parse_ingredientForCRF(ingredients)
    parsData = getNameEntityInIngre(ingreWithNewTAG)
    direWithNewTAG = updateDireTagsAfterCRF(arr, ingreWithNewTAG)

    print(getNameEntityInIngres(ingreWithNewTAG))
    print("----------------------")

    print("----------------------")

    """
    print(ingreWithNewTAG)
    print(direWithNewTAG)
    print(arr)
"""

    print("----------------------")
    for i in xrange(len(direWithNewTAG)):
        direWithNewTAG[i] = utils.checkVerbRemovePrep(direWithNewTAG[i])
        print(direWithNewTAG[i])
        a = [wt for (wt, _) in direWithNewTAG[i] if 'VERB' == _]
        if a == 0:
            direWithNewTAG[i] = updateVerbTagIfVerbIsEmpty(direWithNewTAG[i], giveTheMostCommonTag(direWithNewTAG[i]))

        print("actions")
        print([wt for (wt, _) in direWithNewTAG[i] if 'VERB' == _])
        print("tools ---", [wt for (wt, _) in direWithNewTAG[i] if 'NOUN' == _ or 'ADV' == _])
        toolList = isTool([wt for (wt, _) in direWithNewTAG[i] if 'NOUN' == _ or 'ADV' == _])
        direWithNewTAG[i] = updateForTools(direWithNewTAG[i], toolList)
        if len([wt for (wt, _) in direWithNewTAG[i] if 'VERB' == _]) > 1:
            direWithNewTAG[i] = optimizeTagWithCollocation(direWithNewTAG[i])

        print([wt for (wt, _) in direWithNewTAG[i] if 'TOOL' == _])
        print("ingredients")
        print([wt for (wt, _) in direWithNewTAG[i] if 'NAME' == _])
        if checkDireIfIngredientHasNot(dire[i], parsData):
            print("probable ingedients")
            # add probable ingredient to the newIngres
            ingres = createCosSim(dire[i], parsData, makeFeatureVec(dire[i], model, 300))
            newIngres = []
            if len(ingres) > 0:
                for w in ingres:
                    ing = getSpecificIngredient(w, ingreWithNewTAG)
                    if ing not in newIngres:
                        newIngres.append(ing)
            print(newIngres)
            probablableIngre = " ".join(newIngres)
            direWithNewTAG[i].append((probablableIngre, "PROBABLE"))

        print("units")
        print([wt for (wt, _) in direWithNewTAG[i] if 'UNIT' == _])

        print("comments")
        print([wt for (wt, _) in direWithNewTAG[i] if 'COMMENT' == _])

        print("quantity")
        print([wt for (wt, _) in direWithNewTAG[i] if 'QTY' == _])

        print(direWithNewTAG[i])
        print("----------------------")
    GraphGenerator.GraphGenerator(direWithNewTAG, ingreWithNewTAG).createGraph("result"+str(index)+".dot")


#readData()
#UtilsIO.createPngFromDotFile("result121-3.dot", "result121-3.png")









# cli.Cli(20000, 0).run();

# print lemmatizer.lemmatize('reserving', 'v')
# print wn.synsets('discard')  # .root_hypernyms()


# MODEL SAVED INTO SMALLERFILE & NEXT LOAD FROM IT
# GIVE RESULT SER3!
# print(model['water'])
