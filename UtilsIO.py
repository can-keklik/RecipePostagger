import os, sys


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
    inputFolder = "/Users/ibrahimardic/Documents/RecipesLearning/DataSetOUT"
    outputFolder = "/Users/ibrahimardic/Documents/RecipesLearning/DataSetOUTFreq"
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
