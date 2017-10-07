from __future__ import print_function
from __future__ import print_function
from __future__ import print_function
from __future__ import print_function

from operator import itemgetter

import pandas as pd

import CollocationFinder
import POSTaggerFuncs
import UtilsIO
import WordToVecFunctions
import utils
from nltk.stem import WordNetLemmatizer
from itertools import groupby

from GraphGeneratorForPaper import PaperGraphGenerator
from GraphGeneratorForPaperAnnotated import GraphGeneratorForPaper

lemmatiser = WordNetLemmatizer()
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
    INGREDIENT_TAGS = ["NUM", "COMMENT", "QTY", "ADP", "DET", "UNIT"]
    TOOL_TAGS = ["ADP", "DET", "NOUN", "NUM"]
    VERB_TAG = ["ADP", "DET"]

    def __init__(self, direction):
        self.direction = direction

    def convertTagsAccordingToPaper(self):
        for i in xrange(len(self.direction)):
            sentence = []
            tmp = [(word, k, idx) for k, (word, tag, idx) in enumerate(self.direction[i]) if tag == "NAME"]
            ingredients = []
            a = []
            b = []
            for c, (word, k, idx) in enumerate(tmp):
                a = [(word2, k) for k2, (word2, tag2, idx2) in enumerate(tmp) if idx == idx2]
                b = set([word2 for k2, (word2, tag2, idx2) in enumerate(tmp) if idx == idx2])
                if len(a) > 0 and len(b) > 0:
                    if len(b) == 1:
                        ingredients.extend(a)
                    else:
                        w_tmp = " ".join(s for (s, k3) in a)
                        (s, k3) = a[0]
                        ingredients.append((w_tmp, k3))

            # ingredients = [(word, k) for k, (word, tag, idx) in enumerate(self.direction[i]) if tag == "NAME"]
            tools = [(word, k) for k, (word, tag, idx) in enumerate(self.direction[i]) if tag == "TOOL"]
            verbs = [(word, k) for k, (word, tag, idx) in enumerate(self.direction[i]) if
                     tag == "VERB" and len(word) > 1]
            length_of_sent = len(self.direction[i])
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
        return self.newDirection


def updateActionsForGraphGenearation(directions):
    seen = set()
    retArrAll = []
    for i in xrange(len(directions)):
        direction = directions[i]
        retArr = []
        for (w, t, idx) in direction:
            w_new = ""
            if w not in seen and t == "VERB":
                seen.add(w)
                if chechVerbHasIngSuffix(w):
                    w_new = w
                else:
                    w_new = w  # FALSE_VERB
            elif w in seen and t == "VERB":
                num = addUp(w)
                w_new = w + "_" + str(num)

            else:
                if w_new != FALSE_VERB:
                    w_new = w
            if w_new != FALSE_VERB:
                retArr.append((w_new, t, idx))

        retArrAll.append(retArr)

    return retArrAll


def addUp(word):
    arr = word.split("_")
    if len(arr) == 1:
        return 1
    else:
        return int(arr[1]) + 1


def chechVerbHasIngSuffix(verb):
    lemma_verb = lemmatiser.lemmatize(verb, pos="v")
    return len(lemma_verb) == len(verb)


def optimizeTagWithCollocation(param):
    toolList = [wt.replace(" ", "_") for (wt, _) in param if 'TOOL' == _]
    actionList = [wt for (wt, _) in param if 'VERB' == _]
    toRemove = []
    retArr = []
    if len(toolList) > 0:
        for tool in toolList:
            collList = CollocationFinder.calculateCollocationFromPaper(tool)
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
        for (direW, TAG, idx) in direSent:
            lemma = ""
            try:
                lemma = POSTaggerFuncs.lemmatizer.lemmatize(direW)
            except:
                lemma = ""

            for w in toolList:
                if lemma in w:
                    if (w, "TOOL") not in returnArr:
                        returnArr.append((w, "TOOL", 0))
                else:
                    returnArr.append((direW, TAG, idx))
        return returnArr
    else:
        return direSent


def updateIngreTagInSent(sentence, sentIngreList):
    if len(sentIngreList) == 0:
        return sentence
    ingreUpdatedSentence = []
    remove_item = ()
    for i in xrange(len(sentence)):
        (ws, ts, idxs) = sentence[i]
        ingreList = [wing for (wing, ting, iing) in sentIngreList]
        stringre = " ".join(str(ing) for ing in ingreList)
        if str(ws) in str(stringre):
            for j in xrange(len(sentIngreList)):
                (wi, ti, idxi) = sentIngreList[j]
                if str(ws) in str(wi) and (wi, ti, idxi) not in ingreUpdatedSentence:
                    ingreUpdatedSentence.append((wi, ti, idxi))
                    remove_item = (wi, ti, idxi)
                elif len(ingreUpdatedSentence) > 0:
                    tmp = [wtmp for (wtmp, ttmp, ixtmp) in ingreUpdatedSentence]
                    flag = False
                    str1 = ' '.join(str(e) for e in tmp)
                    if str(ws) not in str(str1) and (ws, ts, idxs) not in ingreUpdatedSentence:
                        flag = True

                    if flag:
                        ingreUpdatedSentence.append((ws, ts, idxs))
                elif (ws, ts, idxs) not in ingreUpdatedSentence:
                    ingreUpdatedSentence.append((ws, ts, idxs))
        else:
            ingreUpdatedSentence.append((ws, ts, idxs))
        sentIngreList = [(we, te, ie) for (we, te, ie) in sentIngreList if (we, te, ie) != remove_item]

        # ingredient is done
    updatedSentence = []
    word = ""
    for i in xrange(len(ingreUpdatedSentence)):
        (wg, tg, idx) = ingreUpdatedSentence[i]
        if tg == 'VERB' and i < len(ingreUpdatedSentence) - 1:
            (w_f, t_f, i_f) = ingreUpdatedSentence[i + 1]
            if t_f == 'ADP':
                word = word + wg + " " + w_f
                updatedSentence.append((word, tg, idx))
                word = ""
            elif i > 1:
                (w_b, t_b, i_b) = ingreUpdatedSentence[i - 1]
                if t_b == 'ADP':
                    word = word + w_b + " " + wg
                    updatedSentence.append((word, tg, idx))
                    word = ""
                else:
                    tmp = [wa for (wa, ta, ix) in updatedSentence]
                    str1 = ' '.join(str(e) for e in tmp)
                    if str(wg) not in str(str1) and (wg, tg, idx) not in updatedSentence:
                        updatedSentence.append((wg, tg, idx))
            else:
                tmp = [wa for (wa, ta, ix) in updatedSentence]
                str1 = ' '.join(str(e) for e in tmp)
                if str(wg) not in str(str1) and (wg, tg, idx) not in updatedSentence:
                    updatedSentence.append((wg, tg, idx))
        else:
            tmp = [wa for (wa, t, ix) in updatedSentence]
            str1 = ' '.join(str(e) for e in tmp)
            if str(wg) not in str(str1) and (wg, tg, idx) not in updatedSentence:
                updatedSentence.append((wg, tg, idx))

    return updatedSentence


def updateIngreTagInSent2(sentence, sentIngreList):
    if len(sentIngreList) == 0:
        return sentence
    ingreUpdatedSentence = []
    INGRE_TAGS_STR = " ".join(str(TAG) for TAG in INGRE_TAGS)
    ingreList = [wing for (wing, ting, iing) in sentIngreList]
    stringre = " ".join(str(ing) for ing in ingreList)
    for i in xrange(len(sentence)):
        (ws, ts, idxs) = sentence[i]
        if str(ws) in str(stringre):
            if str(ts) in str(INGRE_TAGS_STR):
                for j in xrange(len(sentIngreList)):
                    (wi, ti, idxi) = sentIngreList[j]
                    if str(ws) in str(wi) and (wi, ti, idxi) not in ingreUpdatedSentence:
                        ingreUpdatedSentence.append((wi, ti, idxi))
        else:
            ingreUpdatedSentence.append((ws, ts, idxs))
    return ingreUpdatedSentence


def updateVerbTagInSent(ingreUpdatedSentence):
    updatedSentence = []
    word = ""
    for i in xrange(len(ingreUpdatedSentence)):
        (wg, tg, idx) = ingreUpdatedSentence[i]
        if tg == 'VERB' and i < len(ingreUpdatedSentence) - 1:
            (w_f, t_f, i_f) = ingreUpdatedSentence[i + 1]
            if t_f == 'ADP' or t_f == "ADV":
                word = word + wg + " " + w_f
                updatedSentence.append((word, tg, idx))
                word = ""
            elif i > 1:
                (w_b, t_b, i_b) = ingreUpdatedSentence[i - 1]
                if t_b == 'ADP':
                    word = word + w_b + " " + wg
                    updatedSentence.append((word, tg, idx))
                    word = ""
                else:
                    tmp1 = [wa for (wa, ta, ix) in updatedSentence]
                    str1 = ' '.join(str(e) for e in tmp1)
                    if str(wg) not in str(str1) and (wg, tg, idx) not in updatedSentence:
                        updatedSentence.append((wg, tg, idx))
            else:
                tmp2 = [wa for (wa, ta, ix) in updatedSentence]
                str1 = ' '.join(str(e) for e in tmp2)
                if str(wg) not in str(str1) and (wg, tg, idx) not in updatedSentence:
                    updatedSentence.append((wg, tg, idx))
        else:
            tmp3 = [wa for (wa, t, ix) in updatedSentence]
            str1 = ' '.join(str(e) for e in tmp3)
            if str(wg) not in str(str1) and (wg, tg, idx) not in updatedSentence:
                updatedSentence.append((wg, tg, idx))
    return updatedSentence


def unionWordAndUpdateTags(sentence):
    idxes = [idx for (w, t, idx) in sentence if idx != 0]
    names = [w for (w, t, idx) in sentence if t == "NAME"]
    # first union the ingredients
    idxes = list(set(idxes))
    sentIngreList = []
    if len(names) > 0:
        indexes = []
        indexAndId = []
        for i in xrange(len(sentence)):
            (w, t, idi) = sentence[i]
            for name in names:
                if w == name:
                    indexes.append(i)
                    indexAndId.append((i, idi))
        if len(indexes) > 0:
            sizeOfSent = len(sentence)
            addingWord = ""
            for i in xrange(len(indexAndId)):
                (index, idy) = indexAndId[i]
                (word, tag, ix) = sentence[index]
                addingWord = word
                if index > 1 and index < sizeOfSent - 1:
                    x = int(index) - 1
                    stn_tmp = sentence
                    while x >= 0:
                        (w_tpm, t_tmp, i_tmp) = stn_tmp[x]
                        if t_tmp not in NEAR_ING_WHOLE_TAGS:
                            break
                        if t_tmp in NEAR_ING_WHOLE_TAGS:
                            addingWord = w_tpm + " " + addingWord + " "
                        x -= 1
                    (w_f, t_f, i_f) = sentence[index + 1]
                    if t_f == "NAME" and i_f == ix:
                        addingWord = addingWord + w_f

                    sentIngreList.append((addingWord, "INGREDIENT", ix))
                    addingWord = ""
    return updateIngreTagInSent2(sentence=sentence, sentIngreList=sentIngreList)


def updateNounToVerb(noun, sentence):
    retArr = []
    for (wt, _, idx) in sentence:
        if wt == noun:
            retArr.append((wt, "VERB", idx))
        else:
            retArr.append((wt, _, idx))

    return retArr


def findAndUpdateVerbTagInSent(sentence):
    nouns = [wt for (wt, _, idx) in sentence if 'NOUN' == _]

    if len(nouns) > 0:
        noun = CollocationFinder.giveTheMostCommonTagg(nouns)
        return updateNounToVerb(noun, sentence)


def readPaperData(index):
    df = pd.read_csv("/Users/Ozgen/Desktop/RecipeGit/csv/paper.csv", encoding='utf8')
    # names=["index", "title", "ingredients", "directions"])

    ingredients = df.ix[index, :].ingredients.encode('utf8').lower()
    ingredients = (utils.convertArrayToPureStr(ingredients))

    directions = df.ix[index, :].directions.encode('utf8').lower()
    arr = POSTaggerFuncs.posTaggText(directions)
    dire = POSTaggerFuncs.tokenizeText(directions)
    ingreWithNewTAG = POSTaggerFuncs.parse_ingredientForCRF(ingredients)
    parsData = POSTaggerFuncs.getNameEntityInIngre(ingreWithNewTAG)
    direWithNewTAG = POSTaggerFuncs.updateDireTagsAfterCRF(arr, ingreWithNewTAG)
    verbArr = []
    wholeVerbs = []
    taggedNewDire = []
    for i in xrange(len(direWithNewTAG)):
        toolList = isTool([wt for (wt, _, idx) in direWithNewTAG[i] if 'NOUN' == _ or 'ADV' == _])

        direWithNewTAG[i] = updateForTools(direWithNewTAG[i], toolList)
        print(direWithNewTAG[i])
        print("-------------------------------------")
        ingeUpdate = unionWordAndUpdateTags(direWithNewTAG[i])
        newTaggedDirection = updateVerbTagInSent(ingreUpdatedSentence=ingeUpdate)
        print(newTaggedDirection)
        ingArr = [w2 for (w2, t2, ix2) in newTaggedDirection if t2 == "INGREDIENT"]
        tmp = [w for (w, t, ix) in newTaggedDirection if t == "VERB"]
        if len(tmp) == 0:
            newTaggedDirection = findAndUpdateVerbTagInSent(newTaggedDirection)
        if len(tmp) > 0:
            wholeVerbs.append(tmp[0])
        if len(ingArr) == 0 and len(tmp) > 0:
            verbArr.append(tmp[0])
        print("-------------------------------------")
        print("-------------------------------------")
        taggedNewDire.append(newTaggedDirection)
    print("whole verbs", wholeVerbs)
    print("Array verbs", verbArr)
    relatedVerbs = WordToVecFunctions.createCosSim(verbArray=verbArr, wholeVerbs=wholeVerbs)
    print(relatedVerbs)
    directionNew = updateActionsForGraphGenearation(taggedNewDire)
    for i in xrange(len(directionNew)):
        print(directionNew[i])
    return ParsedDirection(directionNew)


def readData2(index):
    df = pd.read_csv("/Users/Ozgen/Desktop/RecipeGit/csv/paper.csv", encoding='utf8')
    # names=["index", "title", "ingredients", "directions"])

    ingredients = df.ix[index, :].ingredients.encode('utf8').lower()
    ingredients = (utils.convertArrayToPureStr(ingredients))

    directions = df.ix[index, :].directions.encode('utf8').lower()
    arr = POSTaggerFuncs.posTaggText(directions)
    dire = POSTaggerFuncs.tokenizeText(directions)
    ingreWithNewTAG = POSTaggerFuncs.parse_ingredientForCRF(ingredients)
    parsData = POSTaggerFuncs.getNameEntityInIngre(ingreWithNewTAG)
    direWithNewTAG = POSTaggerFuncs.updateDireTagsAfterCRF(arr, ingreWithNewTAG)
    verbArr = []
    wholeVerbs = []
    taggedNewDire = []
    for i in xrange(len(direWithNewTAG)):
        toolList = isTool([wt for (wt, _, idx) in direWithNewTAG[i] if 'NOUN' == _ or 'ADV' == _])

        direWithNewTAG[i] = updateForTools(direWithNewTAG[i], toolList)
        ingArr = [w2 for (w2, t2, ix2) in direWithNewTAG[i] if t2 == "NAME"]
        tmp = [w for (w, t, ix) in direWithNewTAG[i] if t == "VERB"]
        if len(tmp) == 0:
            direWithNewTAG[i] = findAndUpdateVerbTagInSent(direWithNewTAG[i])
        if len(tmp) > 0:
            wholeVerbs.append(tmp[0])
        if len(ingArr) == 0 and len(tmp) > 0:
            verbArr.append(tmp[0])
        taggedNewDire.append(direWithNewTAG[i])
    return (ParsedDirection(direWithNewTAG).convertTagsAccordingToPaper())


def createGrapWithIndexForPaper(index):
    data = readPaperData(index=index)
    print(data.relatedVerbs)
    PaperGraphGenerator(data.direction, data.relatedVerbs).createGraph("result" + str(index) + ".dot")
    UtilsIO.createPngFromDotFile("paper/result" + str(index) + ".dot", "paper/result" + str(index) + ".png")


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

        wholeVerbs.add(verbs[0])
        if len(ingres) == 0:
            tmp.add(verbs[0])

    if len(wholeVerbs) > 0 and len(tmp) > 0:
        relatedVerbs = WordToVecFunctions.createCosSim(verbArray=tmp, wholeVerbs=wholeVerbs)
    return relatedVerbs


def createGrapWithIndexForPaper2(index):
    data = readData2(index=index)
    relatedVerbs = getRelatedVerbs(data)
    file_name = "result" + str(index) + ".dot"
    print(relatedVerbs)
    print("---------------------------------")
    for i in xrange(len(data)):
        print(data[i])
    GraphGeneratorForPaper(data, relatedVerbs).createGraph(file_name)
    UtilsIO.createPngFromDotFile("paper/result" + str(index) + ".dot", "paper/result" + str(index) + ".png")


createGrapWithIndexForPaper2(20)
