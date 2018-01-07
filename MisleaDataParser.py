from __future__ import print_function
from __future__ import print_function
from __future__ import print_function
from __future__ import print_function

import os

import pandas as pd

import CollocationFinder
import POSTaggerFuncs
import UtilsIO
import WordToVecFunctions
import utils
from GraphGeneratorForPaperAnnotated import GraphGeneratorForPaper
import math

FALSE_VERB = "FV"
INGRE_TAGS = ["NAME", "UNIT"]
NEW_INGRE_TAG = "INGREDIENT"
ACTION_TAGS = ["VERB", "ADP"]
NEAR_ING_WHOLE_TAGS = ["UNIT", "ADP", "QTY", "COMMENT", "NUM"]

PRED = "PRED"  # verb tag
PRED_PREP = "PRED_PREP"  # verb tag with adp
DOBJ = "DOBJ"  # obj that is not related with ingredient
NON_INGREDIENT_SPAN = "NON_INGREDIENT_SPAN"  # obj that is not related with ingredient
NON_INGREDIENT_SPAN_VERB = "NON_INGREDIENT_SPAN_VERB"  # obj that is not related with ingredient
INGREDIENT_SPAN = "INGREDIENT_SPAN"  # obj that is related with ingredient
INGREDIENTS = "INGREDIENTS"  # pure ingredient
PARG = "PARG"  # tool
PREP = "PREP"  # preposition
PREDID = "PREDID"  # this id is realed with action's order


class ParsedDirection:
    newDirection = []
    PRED = "PRED"  # verb tag
    PRED_PREP = "PRED_PREP"  # verb tag with adp
    DOBJ = "DOBJ"  # obj that is not related with ingredient
    NON_INGREDIENT_SPAN = "NON_INGREDIENT_SPAN"  # obj that is not related with ingredient
    NON_INGREDIENT_SPAN_VERB = "NON_INGREDIENT_SPAN_VERB"  # obj that is not related with ingredient
    INGREDIENT_SPAN = "INGREDIENT_SPAN"  # obj that is related with ingredient
    INGREDIENTS = "INGREDIENTS"  # pure ingredient
    PARG = "PARG"  # tool
    PREP = "PREP"  # preposition
    PREDID = "PREDID"  # this id is realed with action's order
    INGREDIENT_TAGS = ["NUM", "COMMENT", "QTY", "ADP", "DET", "UNIT", "ADJ"]
    TOOL_TAGS = ["ADP", "DET", "NOUN", "NUM", "ADJ", "COMMENT"]
    VERB_TAG = ["ADP", "DET"]

    def __init__(self, direction):
        clean = filter(None, direction)
        self.direction = clean

    def checkTwoNubsIsConsecutive(self, num1, num2):
        return math.fabs((num1 - num2)) == 1

    def convertTagsAccordingToPaper(self):
        for i in xrange(len(self.direction)):
            # each sentence
            if (self.direction is None):
                return
            sentence = []
            tmp = [(word, k, idx) for k, (word, tag, idx) in enumerate(self.direction[i]) if tag == "NAME"]
            ingredients = []
            tools = []
            verbs = []
            a = []
            b = []
            if (len(tmp)):
                for c, (word, k, idx) in enumerate(tmp):
                    a = [(word2, k2) for k3, (word2, k2, idx2) in enumerate(tmp) if idx == idx2]
                    b = set([word2 for k3, (word2, k2, idx2) in enumerate(tmp) if idx == idx2])
                    if len(a) > 0 and len(b) > 0:
                        if len(b) == 1:
                            ingredients.extend(a)
                        else:

                            w_tmp = ""
                            tmp_arr = []
                            w_k = 0
                            for (wrd, k) in a:
                                if len(w_tmp) == 0:
                                    w_tmp = wrd
                                    w_k = k
                                else:
                                    if str(wrd) not in str(w_tmp) and self.checkTwoNubsIsConsecutive(w_k, k):
                                        w_tmp = w_tmp + " " + wrd
                                    else:
                                        tmp_arr.append((wrd, k))

                            if len(w_tmp) > 0 and (w_tmp, w_k) not in tmp_arr:
                                tmp_arr.append((w_tmp, w_k))
                            if len(tmp_arr) > 0:
                                for o in xrange(len(tmp_arr)):
                                    if tmp_arr[o] not in ingredients:
                                        ingredients.append(tmp_arr[o])
            # ingredients = [(word, k) for k, (word, tag, idx) in enumerate(self.direction[i]) if tag == "NAME"]
            tools = [(word, k) for k, (word, tag, idx) in enumerate(self.direction[i]) if tag == "TOOL"]
            verbs = [(word, k) for k, (word, tag, idx) in enumerate(self.direction[i]) if
                     tag == "VERB" and len(word) > 1]
            length_of_sent = len(self.direction[i])
            # print(self.direction[i])
            if len(verbs) > 0:
                (word, k) = verbs[0]
                sentence.append((word, self.PRED, i))
                (wo, tag, idx) = self.direction[i][k + 1]
                if tag == "ADV" or tag == "ADP" or tag == "ADJ" or tag == "PRT":
                    whole_word = word + " " + wo
                    sentence.append((whole_word, self.PRED_PREP, i))
                if len(verbs) > 1:
                    verbs = verbs[1:]
                    for verb in verbs:
                        (word, k) = verb
                        if k < length_of_sent and k > 0:
                            whole_word = word
                            for n in range(k - 1, -1, -1):
                                (wo, tag, idx) = self.direction[i][n]
                                if tag in self.VERB_TAG:
                                    if str(wo) not in str(whole_word):
                                        whole_word = wo + " " + whole_word
                                if tag == "NAME" or tag == "VERB" or tag == "TOOL":
                                    if len(whole_word) >= len(word):
                                        sentence.append((whole_word, self.NON_INGREDIENT_SPAN_VERB, i))
                                        whole_word = ""
                                    break

            if len(ingredients) > 0:
                for ingredient in ingredients:
                    (word, k) = ingredient
                    if (word, self.INGREDIENTS, i) not in sentence:
                        sentence.append((word, self.INGREDIENTS, i))
                    if k < length_of_sent and k > 0:
                        whole_word = word
                        for n in range(k - 1, -1, -1):
                            (wo, tag, idx) = self.direction[i][n]
                            if tag in self.INGREDIENT_TAGS:
                                whole_word = wo + " " + whole_word
                            if tag == "NAME" or tag == "VERB" or tag == "TOOL":
                                if len(whole_word) > len(word):
                                    if (whole_word, self.INGREDIENT_SPAN, i) not in sentence:
                                        sentence.append((whole_word, self.INGREDIENT_SPAN, i))
                                    whole_word = ""
                                break

            if len(tools) > 0:
                for tool in tools:
                    (word, k) = tool
                    if (word, self.PARG, i) not in sentence:
                        sentence.append((word, self.PARG, i))
                    if k < length_of_sent and k > 0:
                        whole_word = word
                        for n in range(k - 1, -1, -1):
                            (wo, tag, idx) = self.direction[i][n]
                            if tag in self.TOOL_TAGS:
                                if str(wo) not in str(whole_word):
                                    whole_word = wo + " " + whole_word
                            if tag == "NAME" or tag == "VERB" or tag == "TOOL":
                                if len(whole_word) > len(word):
                                    if (whole_word, self.NON_INGREDIENT_SPAN, i) not in sentence:
                                        sentence.append((whole_word, self.NON_INGREDIENT_SPAN, i))
                                    whole_word = ""
                                break
                            elif n == 0:
                                if len(whole_word) > len(word):
                                    if (whole_word, self.NON_INGREDIENT_SPAN, i) not in sentence:
                                        sentence.append((whole_word, self.NON_INGREDIENT_SPAN, i))
                                    whole_word = ""
            dobj_str_ingreSpan = " - ".join(w for (w, t, ix) in sentence if t == self.INGREDIENT_SPAN)
            # dobj_str_NoningreSpan = " - ".join(w for (w, t, ix) in sentence if t == self.NON_INGREDIENT_SPAN)
            dobj_str = ""
            # if len(dobj_str_NoningreSpan) > 0:
            #   dobj_str = dobj_str_NoningreSpan
            if len(dobj_str_ingreSpan) > 0:
                dobj_str = dobj_str_ingreSpan
            if len(dobj_str) > 5:
                if (dobj_str, self.DOBJ, i) not in sentence:
                    sentence.append((dobj_str, self.DOBJ, i))
            self.newDirection.append(sentence)
            # print('sentence', sentence)
        return self.newDirection


def isTool(words):
    arr = []
    if (len(words) > 0):
        for i in xrange(len(words)):
            lemma = ""
            if len(str(words[i])) > 2:
                try:
                    lemma = POSTaggerFuncs.lemmatizer.lemmatize(word=words[i])
                except:
                    lemma = ""
                    pass
                arr.append(lemma)

    sentence = " ".join(arr)

    return utils.checkToolList(sentence)


# TODO: we get postagged data array = arr and we will fill actions , ingredients and tool list


def updateForTools(direSent, toolList):
    returnArr = []
    if len(toolList) > 0:
        for i, (direW, TAG, idx) in enumerate(direSent):
            lemma = ""
            try:
                lemma = POSTaggerFuncs.lemmatizer.lemmatize(direW)
            except:
                lemma = ""

            for w in toolList:
                if lemma in w:
                    if (w, "TOOL") not in returnArr:
                        returnArr.append((w, "TOOL", 0))
            if len(returnArr) < i + 1:
                returnArr.append((direW, TAG, idx))
        return returnArr
    else:
        return direSent


def updateNounToVerb(noun, sentence):
    retArr = []
    for (wt, _, idx) in sentence:
        if wt == noun:
            retArr.append((wt, "VERB", idx))
        else:
            retArr.append((wt, _, idx))

    return retArr


def findAndUpdateVerbTagInSent(sentence):
    nouns_adj = [wt for (wt, _, idx) in sentence if 'NOUN' == _ or "ADJ" == _ or "ADV" == _]

    if len(nouns_adj) > 0:
        noun = CollocationFinder.giveTheMostCommonTagg(nouns_adj)
        return updateNounToVerb(noun, sentence)


def convertDirectionToSentenceArray(direction):
    retArr = []
    for i in xrange(len(direction)):
        tmp = " ".join(str(word) for word in direction[i])
        retArr.append(tmp)
    return retArr


def readData2(index):
    df = pd.read_csv("/Users/Ozgen/Desktop/RecipeGit/csv/paper.csv", encoding='utf8')
    # names=["index", "title", "ingredients", "directions"])

    ingredients = df.ix[index, :].ingredients.encode('utf8').lower()
    ingredients = (utils.convertArrayToPureStr(ingredients))

    title = df.ix[index, :].title.encode('utf8').lower()

    directions = df.ix[index, :].directions.encode('utf8').lower()
    arr = POSTaggerFuncs.posTaggText(directions)
    dire = POSTaggerFuncs.tokenizeText(directions)
    sentences = convertDirectionToSentenceArray(direction=dire)
    ingreWithNewTAG = POSTaggerFuncs.parse_ingredientForCRF(ingredients)
    parsData = POSTaggerFuncs.getNameEntityInIngre(ingreWithNewTAG)
    direWithNewTAG = POSTaggerFuncs.updateDireTagsAfterCRF2(arr, ingreWithNewTAG)
    verbArr = []
    wholeVerbs = []
    taggedNewDire = []
    for i in xrange(len(direWithNewTAG)):
        # print(direWithNewTAG[i])
        # print("*---------------------*")
        toolList = isTool([wt for (wt, _, idx) in direWithNewTAG[i] if 'NOUN' == _ or 'ADV' == _])
        direWithNewTAG[i] = updateForTools(direWithNewTAG[i], toolList)
        # print("tool updated", direWithNewTAG[i])
        ingArr = [w2 for (w2, t2, ix2) in direWithNewTAG[i] if t2 == "NAME"]
        tmp = [w for (w, t, ix) in direWithNewTAG[i] if t == "VERB"]
        if len(tmp) == 0:
            direWithNewTAG[i] = findAndUpdateVerbTagInSent(direWithNewTAG[i])
        if len(tmp) > 0:
            wholeVerbs.append(tmp[0])
        if len(ingArr) == 0 and len(tmp) > 0:
            verbArr.append(tmp[0])
        taggedNewDire.append(direWithNewTAG[i])
        # print("*---------------------*")
        # print(direWithNewTAG[i])
        # print("*---------------------*")
    return (ParsedDirection(direWithNewTAG).convertTagsAccordingToPaper(), title, sentences)


def getRelatedVerbs(data):
    wholeVerbs = set()
    tmp = set()
    relatedVerbs = []
    for i in xrange(len(data)):
        sentence = data[i]
        verbs = [w for (w, t, idx) in sentence if t == PRED_PREP]
        ingres = [w for (w, t, idx) in sentence if t == INGREDIENTS]
        if len(verbs) == 0:
            verbs = [w for (w, t, idx) in sentence if t == PRED]
        if len(verbs) > 0:
            wholeVerbs.add(verbs[0])
        if len(ingres) == 0 and len(verbs) > 0:
            tmp.add(verbs[0])

    if len(wholeVerbs) > 0 and len(tmp) > 0:
        relatedVerbs = WordToVecFunctions.createCosSim(verbArray=tmp, wholeVerbs=wholeVerbs)
    return relatedVerbs


def createGrapWithIndexForPaper2(index):
    (data, title, directionSentenceArray) = readData2(index=index)
    relatedVerbs = getRelatedVerbs(data)
    file_name = title + ".dot"
    print(relatedVerbs)
    print("---------------------------------   " + title)
    for i in xrange(len(data)):
        print(data[i])
    GraphGeneratorForPaper(data, relatedVerbs).createGraph(file_name)
    UtilsIO.createPngFromDotFile("paper/" + file_name, "paper/" + title + ".png")
    str_value = "title : " + title + "\n" + "\n"

    for i in xrange(len(data)):
        str_value = str_value + "SENT_ID :" + str(i) + "\n"
        str_value = str_value + "SENTENCE : " + str(directionSentenceArray[i]) + "\n"
        for (word, tag, idx) in data[i]:
            str_value = str_value + str(tag) + " : " + str(word) + "\n"

        str_value = str_value + "\n"
    completeName = os.path.join(os.getcwd() + "/results/text_result/", title + ".txt")
    outFile = open(completeName, 'w')
    # print fileName
    outFile.truncate()
    outFile.write(str_value)
    outFile.close()


def readPaperDataArgCreateGraph(title):
    data = UtilsIO.readPaperDataForGraph("")
    data = [arr for arr in data if len(arr) > 0]
    for sent in data:
        print(sent)
    relatedVerbs = getRelatedVerbs(data)
    print(relatedVerbs)
    file_name = title + ".dot"
    GraphGeneratorForPaper(data, relatedVerbs).createGraph(file_name)
    UtilsIO.createPngFromDotFile("paper/" + file_name, "paper/" + title + ".png")


# readPaperDataArgCreateGraph("trialramenslaw")

#readData2(18)
createGrapWithIndexForPaper2(6)
# todo check 27. recipe for noningredient sentence...
# bug occur in 32
# readData2(0)
