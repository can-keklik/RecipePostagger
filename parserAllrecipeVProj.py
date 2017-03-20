
from BeautifulSoup import BeautifulSoup
import os, shutil
import string
import re
import sys

files = []
globalData = ""
titlesOfRecipes = []
pathOfRecipes = []
fileNames = []


# 1 Title
def getTitle(data, f, path):
    bs = BeautifulSoup(data)
    print f
    ingreds = bs.body.find('h1', attrs={'itemprop': 'name'}).text
    #if ingreds not in titlesOfRecipes:  # eliminate duplicates
    titlesOfRecipes.append(ingreds)
    pathOfRecipes.append(path)
    fileNames.append(f)  # append
    return ingreds


# 2
def getDescription(bs):
    descValue = str(bs.body.find('div', attrs={'class': 'submitter__description'}).text)
    descr = descValue.replace("&#34;", "") + " \n"
    return descr


# 3 Recipe By
def getRecipeBy(bs):
    recipeBy = bs.body.find('span', attrs={'class': 'submitter__name'}).text + " "
    return recipeBy


# 4 Ingredients
def getIngredients(bs):
    ingredient = bs.body.findAll('span', attrs={'class': 'recipe-ingred_txt added'})
    result = ""
    for i in xrange(len(ingredient)):
        result = result + str(ingredient[i].text) + "\n"

    return result + " \n"


# 5 Serving Size
def getServingSize(bs):
    getServingStr = bs.body.find('div', attrs={'class': 'subtext'}).text
    servingSize = str(int(filter(str.isdigit, str(getServingStr)))) + " "
    return servingSize


# 6 Duration
def getDuration(bs):
    # Not all food contain all subset of the following duration, exception handling added.
    duration = ""
    try:
        prepTime = bs.body.find('time', attrs={'itemprop': 'prepTime'}).text + " "
    except:
        prepTime = ""
    try:
        cookTime = bs.body.find('time', attrs={'itemprop': 'cookTime'}).text + " "
    except:
        cookTime = ""
    try:
        totalTime = bs.body.find('time', attrs={'itemprop': 'totalTime'}).text + " "
    except:
        totalTime = ""

    duration = prepTime + cookTime + totalTime + " "
    return duration


# 7 Directions
def getDirections(bs):
    directions = bs.body.findAll('span', attrs={'class': 'recipe-directions__list--item'})
    result = ""
    for i in xrange(len(directions)):
        result = result + str(directions[i].text) + " "
    return result + " \n"


# 8 Nutrition
def getCalorie(bs):
    # Not all food contain all subset of the following nutritions, exception handling added.
    try:
        calorie = bs.body.find('li', attrs={'itemprop': 'calories'}).text + " "
    except:
        calorie = ""
    try:
        fat = bs.body.find('li', attrs={'itemprop': 'fatContent'}).text + " "
    except:
        fat = ""
    try:
        carbs = bs.body.find('li', attrs={'itemprop': 'carbohydrateContent'}).text + " "
    except:
        carbs = ""
    try:
        protein = bs.body.find('li', attrs={'itemprop': 'proteinContent'}).text + " "
    except:
        protein = ""
    try:
        cholosterol = bs.body.find('li', attrs={'itemprop': 'cholesterolContent'}).text + " "
    except:
        cholosterol = ""
    try:
        sodium = bs.body.find('li', attrs={'itemprop': 'sodiumContent'}).text + " "
    except:
        sodium = ""

    return calorie + fat + carbs + protein + cholosterol + sodium + " "


# 9 Categories
def getCategories(bs):
    categoryList = bs.body.findAll('h3', attrs={'class': 'grid-col__h3 grid-col__h3--recipe-grid'})
    result = ""
    for i in xrange(len(categoryList)):
        result = result + (categoryList[i].text) + " "
    return result + " "


# 10 categories
def getUpCategories(bs):
    upCategoryList = bs.body.findAll('span', attrs={'class': 'toggle-similar__title'})
    uc=''
    print len(upCategoryList)
    if len(upCategoryList) > 2:
        upCategoryList.remove(upCategoryList[0])
        upCategoryList.remove(upCategoryList[0])

    for i in xrange(len(upCategoryList)):
        uc = str(upCategoryList[i].text) + '_'

    return uc


def readFiles(fileName):
    f = open(fileName)
    globalData = f.read()
    f.close()
    return globalData


def main():
    reload(sys)
    notFound = 0
    sys.setdefaultencoding('utf8')
    # TODO: the directories should be checked.
    inputFolder = "/Users/Ozgen/Desktop/allrecipes.com/recipe"
    outputFolder = "/Users/Ozgen/Desktop/RecipesLearning/DataSetOUT"
    inputFoldersId = [path for path in os.listdir(inputFolder) if
                      os.path.isdir(os.path.join(inputFolder, path))]  # list of unique id
    inputFoldersTitle = []  # list of titles
    inputElements = []  # list of files to be processed.

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

    # get the list of files in given folder
    emptypath = ''
    removalList = []
  #  print (len(inputFoldersId))
    for indx in xrange(0, len(inputFoldersId)):
        print inputFoldersId[indx]
        direct = inputFolder + "/" + inputFoldersId[indx]
        inputFolderTitle = [path for path in os.listdir(direct) if os.path.isdir(os.path.join(direct, path))]
        inputFoldersTitle.append(inputFolderTitle[0])
        print inputFolderTitle[0]
        inputCheck = os.listdir(direct + '/' + inputFolderTitle[0])

        if (len(inputCheck) >= 0):
            matching = [s for s in inputCheck if "index.html" in s]
            if (len(matching) == 0):
                if 'index' and 'html' in inputCheck:
                    matching2 = [s for s in inputCheck if "index" and "html" in s]
                    inputItem = direct + '/' + inputFolderTitle[0] + '/' + matching2[0]
                    inputElements.append(inputItem)
                    print (inputItem)
                else:
                    notFound = notFound + 1
                    removalList.append(inputFoldersId[indx])

            else:
                inputItem = direct + '/' + inputFolderTitle[0] + '/' + "index.html"
                inputElements.append(inputItem)
                print (inputItem)

    if (len(inputFoldersId)) != (len(inputElements)):
        print ("Error")
        print len(inputFoldersId)
        print len(inputElements)
        print (notFound)

        for item in xrange(len(removalList)):
            inputFoldersId.remove(removalList[item])

    # if("yedek"  not in inputFolders[indx] and "OUT" not in inputFolders[indx]):
    #	for file in os.listdir(inputFolders[indx]):
    #		files.append(inputFolders[indx] + '/' + file) # append fileNames with path info



    # Extract Informations for each unique title of recipes
    for i in xrange(len(inputElements)):
        data = readFiles(inputElements[i])
        title = getTitle(data, inputFoldersId[i], inputElements[i]) + " \n"  # 1 *
        bs = BeautifulSoup(readFiles(inputElements[i]))
        pathRecipe = str(i) + " - " + inputElements[i] + " \n"
       # title = titlesOfRecipes[i] + " \n"  # 1 *
        description = getDescription(bs)  # 2 *
        recipeBy = getRecipeBy(bs)  # 3
        ingredients = getIngredients(bs)  # 4  *
        servingSize = getServingSize(bs)  # 5
        duration = getDuration(bs)  # 6
        directions = getDirections(bs)  # 7 *
        calories = getCalorie(bs)  # 8
        categories = getCategories(bs)  # 9
        upCategories = getUpCategories(bs)  # 10

        resultData = title + description + recipeBy + ingredients + servingSize + duration + directions + calories + categories + upCategories

        resultData = title + description + ingredients + directions + upCategories
       # print pathRecipe + resultData
        # printing data into the new file in outputfolder
        print title
        outFile = open(outputFolder + "/" +upCategories  + "_" + fileNames[i], 'w')
        outFile.truncate()
        outFile.write(resultData.encode('utf8'))
        outFile.close()

        outFile = open(outputFolder + "/" + upCategories + "_" + fileNames[i] + "_ingredients", 'w')
        outFile.truncate()
        outFile.write(ingredients.encode('utf8'))
        outFile.close()

        outFile = open(outputFolder + "/" + upCategories + "_" + fileNames[i] + "_directions", 'w')
        outFile.truncate()
        outFile.write(directions.encode('utf8'))
        outFile.close()


# For Trial Commit
if __name__ == "__main__":
    main()
