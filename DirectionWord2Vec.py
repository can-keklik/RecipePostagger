from __future__ import absolute_import, division, print_function
# for word encoding
import codecs
# regex
import glob
# concurency
import multiprocessing

# dealing with operating system

import os

# pretty printing

import pprint

# regular expression

import re

# nlp tool

import nltk

# word 2 vec

import gensim.models.word2vec as w2v

# dimentionality reduction

import sklearn.manifold

# math

import numpy as np

# parse panda as pd

import pandas as pd


# step 1 process our data

global dire2Vec

import POSTaggerFuncs

def readData(file_name):
    names = ["index", "title", "ingredients", "directions"]
    df = pd.read_csv("/Users/Ozgen/Desktop/RecipeGit/" + file_name, skipinitialspace=True, usecols=names,
                     encoding='utf8')

    return df.directions


def sentenceToWordList(raw):
    clean = re.sub("^a-zA-Z", " ", str(raw))
    words = clean.split()
    words2 =[]
    for word in words:
        if "." in word:
            words2.extend(str(word).lower().split("."))
        else:
            words2.append(str(word).lower())
    return words2


def convertDirectionToSentenceArray(direction):
    retArr = []
    for i in xrange(len(direction)):
        try:
            tmp = " ".join(str(word).encode('utf-8') for word in direction[i])
            retArr.append(tmp)
        except:
            pass

    return retArr


def initModel():
    nltk.download('punkt')  # pretrained tokinezer

    nltk.download('stopwords')

    file_names = sorted(glob.glob('csv/*.csv'))
    corpusRaw = u''
    dataArray = []

    for file_name in file_names:
        dataArray.extend(readData(file_name))

    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    raw_sentences = []

    for direction in dataArray:
        dire = POSTaggerFuncs.tokenizeText(direction)
        raw_sentences.append(convertDirectionToSentenceArray(dire))

    sentences = []

    for raw_sentence in raw_sentences:
        if len(raw_sentence) > 0:
            sentences.append(sentenceToWordList(raw_sentence))

    token_count = sum([len(sentence) for sentence in sentences])
    print("The corpus contains {0:,} tokens".format(token_count))

    # ONCE we have vectors
    # step 3 - build model
    # 3 main tasks that vectors help with
    # DISTANCE, SIMILARITY, RANKING

    # Dimensionality of the resulting word vectors.
    # more dimensions, more computationally expensive to train
    # but also more accurate
    # more dimensions = more generalized
    num_features = 300
    # Minimum word count threshold.
    min_word_count = 3

    # Number of threads to run in parallel.
    # more workers, faster we train
    num_workers = multiprocessing.cpu_count()

    # Context window length.
    context_size = 7

    # Downsample setting for frequent words.
    # 0 - 1e-5 is good for this
    downsampling = 1e-3

    # Seed for the RNG, to make the results reproducible.
    # random number generator
    # deterministic, good for debugging
    seed = 1
    direction2Vec = w2v.Word2Vec(
        sg=1,
        seed=seed,
        workers=num_workers,
        size=num_features,
        min_count=min_word_count,
        window=context_size,
        sample=downsampling
    )

    direction2Vec.build_vocab(sentences)

    if not os.path.exists("trained"):
        os.makedirs("trained")

    direction2Vec.save(os.path.join("trained", "direction2vec.w2v"))


def loadModel():
    dire2vec = w2v.Word2Vec.load(os.path.join("trained", "direction2vec.w2v"))
    return dire2vec




def nearest_similarity_cosmul(start1, end1, end2):
    similarities = dire2Vec.most_similar_cosmul(
        positive=[end2, start1],
        negative=[end1]
    )
    start2 = similarities[0][0]
    print("{start1} is related to {end1}, as {start2} is related to {end2}".format(**locals()))
    return start2

dire2Vec = loadModel()

print(nearest_similarity_cosmul("preheat", "bake", "mix"))