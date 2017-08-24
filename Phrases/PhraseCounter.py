import os
import string
import tempfile

import pandas as pd

import utils
from collections import Counter


def parse_ingredientForCRF(ingredients):
    returnArr = []
    eachIngre = []
    _, tmpFile = tempfile.mkstemp()
    _, tmpFile2 = tempfile.mkstemp()
    with open(tmpFile, 'w') as outfile:
        outfile.write(utils.export_data(ingredients))
        outfile.close()
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
    f.close()
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


def readIngredient(index):
    #:todo change file path according to your file
    df = pd.read_csv("/Users/Ozgen/Desktop/RecipeGit/csv/output.csv", encoding='utf8')

    ingredients = df.ix[index, :].ingredients.encode('utf8')
    ingredients = (utils.convertArrayToPureStr(ingredients))
    ingreWithNewTAG = parse_ingredientForCRF(ingredients)
    retArray = []
    for ingredient in ingreWithNewTAG:
        phrased_word = " "
        retArdataray = [w for (w, tag) in ingredient if tag == "NAME" or tag =="COMMENT"]
        phrase = phrased_word.join(str(s) for s in retArdataray if len(retArdataray)>1)
        if len(phrase)>1:
            retArray.append(phrase)

    return retArray

def get_whole_ingredient():
    retArr = []
    for i in range(9000,10000):
        arr = readIngredient(i)
        cap_words = [word.upper() for word in arr]
        retArr.extend(cap_words)
    return retArr

def calculatePhrases(filename):
    cap_words = get_whole_ingredient()
    word_counts = list(Counter(cap_words).items())
    word_counts = sorted(word_counts, key=lambda x: x[1])
    f = open(filename, 'w')
    for (t, c) in word_counts:
        f.write(t+ " - "+str(c) + ' \n')
    f.close()


calculatePhrases("test11.txt")