# MLP for Pima Indians Dataset with 10-fold cross validation
from keras.models import Sequential
from keras.preprocessing.sequence import pad_sequences
from keras.layers import LSTM, Embedding, TimeDistributed, Bidirectional
from keras.layers import Dense
import sklearn.model_selection.KFold as KFold
from sklearn.model_selection import StratifiedKFold
import numpy
import keras.backend as K

# fix random seed for reproducibility
import UtilsIO


def f1_score(y_true, y_pred):
    # Count positive samples.
    c1 = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    c2 = K.sum(K.round(K.clip(y_pred, 0, 1)))
    c3 = K.sum(K.round(K.clip(y_true, 0, 1)))

    # If there are no true samples, fix the F1 score at 0.
    if c3 == 0:
        return 0

    # How many selected items are relevant?
    precision = c1 / c2

    # How many relevant items are selected?
    recall = c1 / c3

    # Calculate f1_score
    f1_score = 2 * (precision * recall) / (precision + recall)
    return f1_score


def precision_val(y_true, y_pred):
    # Count positive samples.
    c1 = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    c2 = K.sum(K.round(K.clip(y_pred, 0, 1)))
    # How many selected items are relevant?
    precision = c1 / c2

    return precision


def recall_val(y_true, y_pred):
    # Count positive samples.
    c1 = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    c3 = K.sum(K.round(K.clip(y_true, 0, 1)))

    # If there are no true samples, fix the F1 score at 0.
    if c3 == 0:
        return 0

    recall = c1 / c3

    # Calculate f1_score
    return recall

seed = 7
numpy.random.seed(seed)
# load pima indians dataset
arr = UtilsIO.readIngredientData()
arr = arr[0:180000]
words = []
tags = []

for ingre in arr:
    for w, t in ingre:
        words.append(w)
        tags.append(t)

n_words = len(words);
n_tags = len(tags);

word2idx = {w: i for i, w in enumerate(words)}
tag2idx = {t: i for i, t in enumerate(tags)}
"""
X = [[word2idx[w[0]] for w in s] for s in arr]
max_len = max([len(x) for x in X])
X = pad_sequences(maxlen=max_len, sequences=X, padding="post", value=n_words - 1)

y = [[tag2idx[w[1]] for w in s] for s in arr]

y = pad_sequences(maxlen=max_len, sequences=y, padding="post")
# define 10-fold cross validation test harness
c, r = y.shape
y = y.reshape(c,)

kfold = StratifiedKFold(n_splits=10, shuffle=True, random_state=seed)
cvscores = []

for train, test in kfold.split(X=X, y=y):
  # create model
    model = Sequential()
    model.add(Embedding(input_dim=n_words, output_dim=50, input_length=max_len))
    model.add(Bidirectional(LSTM(units=100, return_sequences=True, recurrent_dropout=0.1)))
    model.add(TimeDistributed(Dense(n_tags, activation="softmax")))

    model.summary()

    model.compile(optimizer="rmsprop", loss="categorical_crossentropy",
                metrics=['accuracy', f1_score, precision_val, recall_val])

    history = model.fit(numpy.array(X), numpy.array(y), batch_size=32, epochs=1, verbose=1)

    print(history.history.keys())
    scores = model.evaluate(X[test], y[test], verbose=0)
    print("%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))
    cvscores.append(scores[1] * 100)
print("%.2f%% (+/- %.2f%%)" % (numpy.mean(cvscores), numpy.std(cvscores)))
"""


kfold = KFold(3, True, 1)
print(kfold, "kfodl")
for train, test in kfold.split(arr):
	print('train: %s, test: %s' % (train, test))
