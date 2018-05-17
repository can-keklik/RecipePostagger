import nltk
import pandas as pd
from nltk.parse.stanford import StanfordDependencyParser
import POSTaggerFuncs
import utils

"""https://nlp.stanford.edu/software/lex-parser.shtml"""

path_to_jar = 'stanford-parser/stanford-parser.jar'
path_to_models_jar = 'stanford-parser/stanford-parser-3.8.0-models.jar'

"""'I would dip each slice of bread into egg mixture until well soaked , about 20 seconds per side.'"""
"""((u'grease', u'NN'), u'dep', (u'pot', u'VBZ'))"""


def parseSentenceWithDependencyParser(sentence):
    dependency_parser = StanfordDependencyParser(path_to_jar=path_to_jar, path_to_models_jar=path_to_models_jar)
    result = dependency_parser.raw_parse(sentence=" I would " + sentence)
    dep = result.next()
    arr = list(dep.triples())
    arr = [((w1, t1), dep, (w2, t2)) for ((w1, t1), dep, (w2, t2)) in arr
           if w1 != "I" and w2 != "would" and w1 != "would" and w2 != "I"]
    return arr


def readData(index):
    df = pd.read_csv("/Users/Ozgen/Desktop/RecipeGit/csv/paper.csv", encoding='utf8')
    # names=["index", "title", "ingredients", "directions"])

    ingredients = df.ix[index, :].ingredients.encode('utf8').lower()
    ingredients = (utils.convertArrayToPureStr(ingredients))
    title = df.ix[index, :].title.encode('utf8').lower()

    directions = df.ix[index, :].directions.encode('utf8').lower()
    arr = POSTaggerFuncs.posTaggText(directions)
    sentences = nltk.sent_tokenize(directions)

    for sentence in sentences:
        print(sentence)
        print("---------------------------")
        print(parseSentenceWithDependencyParser(sentence))
        print("---------------------------")
    print("---------------------------")
    for s in arr:
        print(s)


readData(0)
