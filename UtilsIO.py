import os
import shutil
import sys

import pandas as pd
import pydot
import unicodecsv as csv

import utils


def readFiles(fileName):
    f = open(fileName)
    globalData = f.read()
    f.close()
    return globalData


def writeFile(fileName, data):
    if (".DS_Store" not in fileName):
        outFile = open(fileName, 'w')
        # print fileName
        outFile.truncate()
        outFile.write(data.encode('utf8'))
        outFile.close()


def getFileList():
    files = []
    reload(sys)
    sys.setdefaultencoding('utf8')
    # TODO: the directories should be checked.
    inputFolder = "/Users/Ozgen/Desktop/RecipesLearning2/DataSetOUT"
    outputFolder = "/Users/Ozgen/Desktop/RecipesLearning2/DataSetOUTFreq"
    # check output directory if not exist, then create it
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)
    else:  # otherwise clear all content of the output folder
        for the_file in os.listdir(outputFolder):
            file_path = os.path.join(outputFolder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)

    for file in os.listdir(inputFolder):
        files.append(inputFolder + '/' + file)  # append fileNames with path info

    return files


def getDataFromPath(filepath):
    returnArr = []
    pathArray = filepath.split('/')
    fileName = pathArray[len(pathArray) - 1]
    splittedFileNameArray = fileName.split('_')
    if (splittedFileNameArray[len(splittedFileNameArray) - 1].isdigit()):
        data = readFiles(filepath)
        output = data.split('\n')
        if (len(output) > 0):
            title = output[0];
            dataToParse = output[2:]
            dataToParse = dataToParse[:len(dataToParse) - 1]
            ingredients = dataToParse[: len(dataToParse) - 1]
            directions = dataToParse[len(dataToParse) - 1]
            returnArr = [title, ingredients, directions]
    return returnArr


def writeWholeDataToCvsFile():
    with open("output.csv", 'wb') as resultFile:
        writer = csv.DictWriter(resultFile, fieldnames=["index", "title", "ingredients", "directions"])
        writer.writeheader()
        wr = csv.writer(resultFile)
        fileList = getFileList()
        if len(fileList) > 0:
            data = []
            cnt = 0;
            for i in xrange(len(fileList)):
                dataToWrite = getDataFromPath(fileList[i])
                if len(dataToWrite) > 2:
                    cnt = cnt + 1
                    data.append([cnt, dataToWrite[0], dataToWrite[1], dataToWrite[2]])
            wr.writerows(data)


def createPngFromDotFile(dotFileName, pngName):
    path = os.getcwd()
    if dotFileName:
        path = path + "/results/"
        (graph,) = pydot.graph_from_dot_file(path + dotFileName)
        graph.write_png(path + pngName)


def getFileList(folderPath, contained_word):
    reload(sys)
    sys.setdefaultencoding('utf8')
    retArr = []
    for dirpath, dirnames, filenames in os.walk(folderPath):
        for filename in [f for f in filenames if str(os.path.join(dirpath, f)).__contains__(contained_word)]:
            retArr.append(os.path.join(dirpath, filename))
    return retArr;


def readMisleaDataFromPath(file_path):
    file_path = file_path


def writePaperDataToCvsFile():
    with open("paper.csv", 'wb') as resultFile:
        writer = csv.DictWriter(resultFile, fieldnames=["index", "title", "ingredients", "directions"])
        writer.writeheader()
        wr = csv.writer(resultFile)
        fileList = getFileList("/Users/Ozgen/Desktop/dataset/AnnotationSession", "fulltext")
        if len(fileList) > 0:
            data = []
            cnt = 0;
            for i in xrange(len(fileList)):
                dataToWrite = getPaperDataFromPath(fileList[i])
                if len(dataToWrite) > 2:
                    cnt = cnt + 1
                    data.append([cnt, dataToWrite[0], dataToWrite[1], dataToWrite[2]])
            wr.writerows(data)


def getPaperDataFromPath(filepath):
    lastPartPoint = "Data Parsed from this"
    directionStartPoint = "Steps"
    ingredientStartPoint = "Ingredients"
    ingredientEndPoint = "Data Parsed from this"
    # dummyPath = "/Users/Ozgen/Desktop/dataset/AnnotationSession/AnnotationSession-fulltext/beer-and-bourbon-pulled-pork-sandwiches.txt"
    returnArr = []
    data = readFiles(filepath)
    output = data.split('\n')
    # output = [w for w in output if len(w)>0]
    startPointOfDirection = 0
    startPointOfIngre = 0
    endPointOfIngre = 0
    for i in xrange(len(output)):
        # print i,output[i]
        if output[i] == directionStartPoint:
            startPointOfDirection = i
        elif output[i] == ingredientStartPoint:
            startPointOfIngre = i
        elif output[i].__contains__(ingredientEndPoint):
            endPointOfIngre = i

    title = output[0]
    directions = output[startPointOfDirection + 1:startPointOfIngre]
    newDirection = ""
    newWord = ""
    for w in directions:
        if len(w) > 0:
            newWord = newWord + w + " "
        elif len(w) == 0:
            newDirection = newDirection + newWord
            newWord = ""
    ingredients = output[startPointOfIngre + 1:endPointOfIngre]
    ingredients = [w for w in ingredients if len(w) > 0]
    returnArr = [title, ingredients, newDirection]
    return returnArr


def readPaperData(index):
    df = pd.read_csv("/Users/Ozgen/Desktop/RecipeGit/csv/paper.csv", encoding='utf8')
    # names=["index", "title", "ingredients", "directions"])

    ingredients = df.ix[index, :].ingredients.encode('utf8')
    ingredients = (utils.convertArrayToPureStr(ingredients))
    directions = df.ix[index, :].directions.encode('utf8')

    print directions


def readPaperDataForGraph(full_path):
    dummyPath = "/Users/Ozgen/Desktop/dataset/AnnotationSession/AnnotationSession-args/amish-meatloaf.txt"
    data = readFiles(dummyPath)
    array = data.split("SENTID")
    arr = []
    for a in array:
        eachSent = a.split("\n")
        params = []
        for param in eachSent:
            if "PREDID:" in str(param):
                tmp = param.split("PREDID:")
                params.append(("PREDID", tmp[1]))
            elif "PRED" in str(param):
                tmp = param.split("PRED:")
                params.append(("PRED", tmp[1]))
            elif "DOBJ" in str(param):
                tmp = param.split("DOBJ:")
                params.append(("DOBJ", tmp[1]))
            elif "NON-INGREDIENT SPAN" in str(param):
                tmp = param.split("NON-INGREDIENT SPAN:")
                params.append(("NON_INGREDIENT_SPAN", tmp[1]))
            elif "INGREDIENT SPAN" in str(param):
                tmp = param.split("INGREDIENT SPAN:")
                params.append(("INGREDIENT_SPAN", tmp[1]))
            elif "INGREDIENTS" in str(param):
                tmp = param.split("INGREDIENTS:")
                params.append(("INGREDIENTS", tmp[1]))
            elif "PARG" in str(param):
                tmp = param.split("PARG:")
                params.append(("PARG", tmp[1]))
            elif "PREP" in str(param):
                tmp = param.split("PREP:")
                params.append(("PREP", tmp[1]))

        arr.append(params)
    return arr

print readPaperDataForGraph("")

# readPaperData(13)
# writePaperDataToCvsFile()
# getPaperDataFromPath("")
# print getFileList("/Users/Ozgen/Desktop/dataset/AnnotationSession","fulltext")[0]

# print readMisleaDataFromPath("/Users/Ozgen/Desktop/dataset/BananaMuffins/BananaMuffins-steps/vegan-banana-muffins.txt")
