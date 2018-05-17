import os

import pandas as pd
import sys

import MisleaDataParser
import POSTaggerFuncs
import UtilsIO
import utils

RESULTS_URL = "/Users/Ozgen/Desktop/RecipeGit/results/paper_general_data/BananaMuffins/BananaMuffins-chunked"
FULLTEXT_URL = "/Users/Ozgen/Desktop/RecipeGit/results/paper_general_data/BananaMuffins/BananaMuffins-fulltext"


def parseRecipeDataFromFile(recipe_txt, fulltext_url=FULLTEXT_URL, result_url=RESULTS_URL):
    directions_not_tokenized = []
    ingredients = []
    ingreWithNewTAG = []
    direWithNewTAG = []
    """
    index = 0
    recipe_name = str(recipe_file_name).split(".txt")[0]
   for i, val in enumerate(df.title):
        if val == recipe_name:
            index = i
            break
    ingredients = df.ix[index, :].ingredients.encode('utf8').lower()
    ingredients = (utils.convertArrayToPureStr(ingredients))

    title = df.ix[index, :].title.encode('utf8').lower() 
    print("title",title, index)
    directions = df.ix[index, :].directions.encode('utf8').lower()"""
    path_full = os.path.join(fulltext_url, recipe_txt)
    path_res = os.path.join(result_url, recipe_txt)
    directions_not_tokenized = UtilsIO.readPaperRecipeForDirection(path_res)
    ingredients = UtilsIO.getIngredientDataFromPath(path_full)
    ingredients = (utils.convertArrayToPureStr(str(ingredients)))

    arr = []
    for sentence in directions_not_tokenized:
        postagged = POSTaggerFuncs.posTaggSent(sentence)
        arr.append(postagged)
    ingreWithNewTAG = POSTaggerFuncs.parse_ingredientForCRF(ingredients)
    direWithNewTAG = POSTaggerFuncs.updateDireTagsAfterCRF2(arr, ingreWithNewTAG)
    for i in xrange(len(direWithNewTAG)):
        toolList = []
        toolList = MisleaDataParser.isTool([wt for (wt, _, idx) in direWithNewTAG[i] if 'NOUN' == _ or 'ADV' == _])
        direWithNewTAG[i] = MisleaDataParser.updateForTools(direWithNewTAG[i], toolList)
        tmp = []
        tmp = [w for (w, t, ix) in direWithNewTAG[i] if t == "VERB"]
        if len(tmp) == 0:
            direWithNewTAG[i] = MisleaDataParser.findAndUpdateVerbTagInSent(direWithNewTAG[i])
    str_value = ""
    data = []
    parsedDirection = MisleaDataParser.ParsedDirection(direWithNewTAG)
    data = parsedDirection.convertTagsAccordingToPaper()
    recipe_name = str(recipe_txt).split(".txt")[0]
    str_value = "title : " + recipe_name + "\n" + "\n"
    for i in xrange(len(data)):
        str_value = str_value + "SENT_ID :" + str(i) + "\n"
        str_value = str_value + "SENTENCE : " + str(directions_not_tokenized[i]) + "\n"
        for (word, tag, idx) in data[i]:
            str_value = str_value + str(tag) + " : " + str(word) + "\n"
        str_value = str_value + "\n"

    print(str_value)

    output_folder_name = "our_model_result"
    tmp = os.path.join(result_url, "../")
    path_to_write = os.path.join(tmp, output_folder_name)
    if not os.path.exists(path_to_write):
        os.makedirs(path_to_write)

    completeName = os.path.join(path_to_write, recipe_txt)
    outFile = open(completeName, 'w')
    # print fileName
    outFile.truncate()
    outFile.write(str_value)
    outFile.close()


def runParser(result_url):
    filenames = os.listdir(result_url)
    for filename in filenames:
        print(filename)
        parseRecipeDataFromFile(filename)


runParser(RESULTS_URL)
# parseRecipeDataFromCsvFile("paper_general.csv", "easy-slow-cooker-apple-pork-roast.txt")
