import nltk
from nltk import FreqDist
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import os , shutil
import string
import re
import sys

files = []

titlesOfRecipes = []
pathOfRecipes = []
fileNames = []
translate_table = dict((ord(char), None) for char in string.punctuation) 


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


def main():
	reload(sys)  
	sys.setdefaultencoding('utf8')
	# TODO: the directories should be checked.
	inputFolder = "/Users/ibrahimardic/Documents/RecipesLearning/DataSetOUT"
	outputFolder = "/Users/ibrahimardic/Documents/RecipesLearning/DataSetOUTFreq"
	globalData = ""
	lemmatizer 	= WordNetLemmatizer()
	stemmer = PorterStemmer()
	stopwords = nltk.corpus.stopwords.words('english')

	# check output directory if not exist, then create it
	if not os.path.exists(outputFolder):
		os.makedirs(outputFolder)
	else: # otherwise clear all content of the output folder
		for the_file in os.listdir(outputFolder):
			file_path = os.path.join(outputFolder, the_file)
			try:
				if os.path.isfile(file_path):
					os.unlink(file_path)
				elif os.path.isdir(file_path): shutil.rmtree(file_path)
			except Exception as e:
				print(e)


	for file in os.listdir(inputFolder):
		files.append(inputFolder + '/' + file) # append fileNames with path info
		fileNames.append(file)
	
	#del files[:]
	#files.append("/Users/ibrahimardic/Documents/RecipesLearning/DataSetOUT/238603")
	#del fileNames[:]
	#fileNames.append("238603")

   	for i in xrange (len(files)):
		if (".DS_Store" not in files[i]):
			data = readFiles(files[i]) # here data is read from the file
			#print data
			print files[i]
			removedPunctiationsData = data.translate(None, string.punctuation)
			# TOKENS
			globalData = globalData  + data + " \n"
			try:
				tokens  = nltk.word_tokenize(data)
			except:
				tokens  = nltk.word_tokenize(data.decode('utf-8'))
		
			fdist = FreqDist(tokens)
			tokenizerStr = ""
			for fd in fdist:
				tokenizerStr = tokenizerStr +  fd + "," + str(fdist[fd]) + "\n"
				#print tokenizerStr

			writeFile(outputFolder + "/" + fileNames[i] + "_tokens.txt", tokenizerStr)
			
			# REMOVE PUNC
			data  = removedPunctiationsData
			tokens  = nltk.word_tokenize(data)
			
			fdist = FreqDist(tokens)
			tokenizerStr = ""
			for fd in fdist:
				tokenizerStr = tokenizerStr +  fd + "," + str(fdist[fd]) + "\n"
				#print tokenizerStr

			writeFile(outputFolder + "/" + fileNames[i] + "_noPunc.txt", tokenizerStr)


			# LOWER
			lowerTokens = [token.lower() for token in tokens]
			stops = [w for w in lowerTokens if w not in stopwords]
			lemmas = [lemmatizer.lemmatize(t) for t in stops]
			try:
				stems = [stemmer.stem(t) for t in stops]
			except:
				stems = [stemmer.stem(t.decode('utf-8')) for t in stops]


			lowerfdist = FreqDist(lowerTokens)
			tokenizerStr = ""
			lemmaStr = ""
			for fd in lowerfdist:
				tokenizerStr = tokenizerStr +  fd + "," + str(lowerfdist[fd]) + "\n"
				#print tokenizerStr
			
			writeFile(outputFolder + "/" + fileNames[i] + "_lowerTokens.txt", tokenizerStr)

			# STOPS
			stopFdist = FreqDist(stops)
			tokenizerStr = ""
			for fd in stopFdist:
				tokenizerStr = tokenizerStr +  fd + "," + str(stopFdist[fd]) + "\n"
				#print tokenizerStr

			writeFile(outputFolder + "/" + fileNames[i] + "_stopWordElm.txt", tokenizerStr)
			# LEMMAS
			lemmaFdist = FreqDist(lemmas)
			tokenizerStr = ""
			for fd in lemmaFdist:
				tokenizerStr = tokenizerStr +  fd + "," + str(lemmaFdist[fd]) + "\n"
				#print tokenizerStr

			writeFile(outputFolder + "/" + fileNames[i] + "_lemmas.txt", tokenizerStr)
            # STEMMER
			stemFdist = FreqDist(stems)
			tokenizerStr = ""
			for fd in stemFdist:
				tokenizerStr = tokenizerStr +  fd + "," + str(stemFdist[fd]) + "\n"
				#print tokenizerStr

			writeFile(outputFolder + "/" + fileNames[i] + "_stems.txt", tokenizerStr)



	#globalData = globalData.decode('utf-8')

	try:
		globalTokens  = nltk.word_tokenize(globalData)
	except:
		globalTokens  = nltk.word_tokenize(globalData.decode('utf-8'))


	fdistGlobal = FreqDist(globalTokens)
	tokenizerStr = ""
	for fd in fdistGlobal:
		tokenizerStr = tokenizerStr +  fd + "," + str(fdistGlobal[fd]) + "\n"
		#print tokenizerStr
	writeFile(outputFolder + "/GlobalTokens.txt", tokenizerStr)

# global dAta output
	# REMOVE PUNC

	globalData  = globalData.translate(None, string.punctuation)
	tokens  = nltk.word_tokenize(globalData)
	
	fdist = FreqDist(tokens)
	tokenizerStr = ""
	for fd in fdist:
		tokenizerStr = tokenizerStr +  fd + "," + str(fdist[fd]) + "\n"
		#print tokenizerStr

	writeFile(outputFolder + "/GlobalNoPunc.txt", tokenizerStr)


	# LOWER
	lowerTokens = [token.lower() for token in tokens]
	stops = [w for w in lowerTokens if w not in stopwords]
	lemmas = [lemmatizer.lemmatize(t) for t in stops]
	try:
		stems = [stemmer.stem(t) for t in stops]
	except:
		stems = [stemmer.stem(t.decode('utf-8')) for t in stops]

	lowerfdist = FreqDist(lowerTokens)
	tokenizerStr = ""
	lemmaStr = ""
	for fd in lowerfdist:
		tokenizerStr = tokenizerStr +  fd + "," + str(lowerfdist[fd]) + "\n"
		#print tokenizerStr
	print "Writing Global Lower"
	writeFile(outputFolder + "/GlobalLowerTokens.txt", tokenizerStr)

	# STOPS
	stopFdist = FreqDist(stops)
	tokenizerStr = ""
	for fd in stopFdist:
		tokenizerStr = tokenizerStr +  fd + "," + str(stopFdist[fd]) + "\n"
		#print tokenizerStr
	print "Written StopWord Lower"
	writeFile(outputFolder + "/GlobalStopWordElm.txt", tokenizerStr)
	# LEMMAS
	lemmaFdist = FreqDist(lemmas)
	tokenizerStr = ""
	for fd in lemmaFdist:
		tokenizerStr = tokenizerStr +  fd + "," + str(lemmaFdist[fd]) + "\n"
		#print tokenizerStr
	print "Written Lemma"

	writeFile(outputFolder + "/GlobalLemmas.txt", tokenizerStr)
    # STEMMER
	stemFdist = FreqDist(stems)
	tokenizerStr = ""
	for fd in stemFdist:
		tokenizerStr = tokenizerStr +  fd + "," + str(stemFdist[fd]) + "\n"
		#print tokenizerStr
	print "Writing Stemm"
	writeFile(outputFolder + "/GlobalStems.txt", tokenizerStr)
# end global data

		
#
if __name__=="__main__":
    main()