from __future__ import print_function
from __future__ import print_function
from __future__ import print_function
from __future__ import print_function
import pandas as pd

import CollocationFinder
import POSTaggerFuncs
import utils
from nltk.stem import WordNetLemmatizer

from GraphGeneratorForPaper import PaperGraphGenerator

lemmatiser = WordNetLemmatizer()
FALSE_VERB = "FV"
INGRE_TAGS = ["NAME", "UNIT"]
NEW_INGRE_TAG = "INGREDIENT"
ACTION_TAGS = ["VERB", "ADP"]
NEAR_ING_WHOLE_TAGS = ["UNIT", "ADP", "QTY", "COMMENT", "NUM"]


def updateActionsForGraphGenearation(directions):
    seen = set()
    retArrAll = []
    for i in xrange(len(directions)):
        direction = directions[i]
        retArr = []
        for (w, t) in direction:
            w_new = ""
            if w not in seen and t == "VERB":
                seen.add(w)
                if chechVerbHasIngSuffix(w):
                    w_new = w
                else:
                    w_new = FALSE_VERB
            elif w in seen and t == "VERB":
                num = addUp(w)
                w_new = w + "_" + str(num)

            else:
                if w_new != FALSE_VERB:
                    w_new = w
            if w_new != FALSE_VERB:
                retArr.append((w_new, t))

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
            lemma = POSTaggerFuncs.lemmatizer.lemmatize(word=words[i])
            arr.append(lemma)

    sentence = " ".join(arr)

    return utils.checkToolList(sentence)


# TODO: we get postagged data array = arr and we will fill actions , ingredients and tool list


def updateForTools(direSent, toolList):
    returnArr = []

    if len(toolList) > 0:
        for (direW, TAG, idx) in direSent:
            lemma = POSTaggerFuncs.lemmatizer.lemmatize(direW)
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

    for i in xrange(len(direWithNewTAG)):
        toolList = isTool([wt for (wt, _, idx) in direWithNewTAG[i] if 'NOUN' == _ or 'ADV' == _])

        direWithNewTAG[i] = updateForTools(direWithNewTAG[i], toolList)
        print(direWithNewTAG[i])
        print("-------------------------------------")
        print(unionWordAndUpdateTags(direWithNewTAG[i]))
        ingArr = [w for (w, t, ix) in direWithNewTAG[i] if t == "INGREDIENT"]
        print("-------------------------------------")
        print("-------------------------------------")


readPaperData(0)
