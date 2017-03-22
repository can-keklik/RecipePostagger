import os, sys, shutil
import unicodecsv as csv
import pandas as pd


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
            for i in xrange(len(fileList)):
                dataToWrite = getDataFromPath(fileList[i])
                if len(dataToWrite) > 2:
                    data.append([i, dataToWrite[0], dataToWrite[1], dataToWrite[2]])
            wr.writerows(data)

writeWholeDataToCvsFile()