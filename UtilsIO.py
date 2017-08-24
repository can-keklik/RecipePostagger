import os
import shutil
import sys

import pydot
import unicodecsv as csv


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
        fileList = getFileList("/Users/Ozgen/Desktop/dataset/AnnotationSession","fulltext")
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
    directionStartPoint ="Steps"
    ingredientStartPoint ="Ingredients"
    ingredientEndPoint = "Data Parsed from this"
    #dummyPath = "/Users/Ozgen/Desktop/dataset/AnnotationSession/AnnotationSession-fulltext/amish-meatloaf.txt"
    returnArr = []
    data = readFiles(filepath)
    output = data.split('\n')
    output = [w for w in output if len(w)>0]
    startPointOfDirection = 0
    startPointOfIngre = 0
    endPointOfIngre = 0
    for i in xrange(len(output)):
        if output[i] == directionStartPoint:
            startPointOfDirection = i
        elif output[i]== ingredientStartPoint:
            startPointOfIngre = i
        elif output[i].__contains__(ingredientEndPoint):
            endPointOfIngre = i

    title = output[0]
    directions = output[startPointOfDirection+1:startPointOfIngre]
    ingredients = output[startPointOfIngre+1:endPointOfIngre]
    returnArr = [title, ingredients, directions]
    return returnArr



#writePaperDataToCvsFile()
#print getFileList("/Users/Ozgen/Desktop/dataset/AnnotationSession","fulltext")[0]

#print readMisleaDataFromPath("/Users/Ozgen/Desktop/dataset/BananaMuffins/BananaMuffins-steps/vegan-banana-muffins.txt")