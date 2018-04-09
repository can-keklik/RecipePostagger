import UtilsIO
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from keras.models import Model, Input
from keras.layers import LSTM, Embedding, Dense, TimeDistributed, Dropout, Bidirectional
from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout
from keras_contrib.layers import CRF

import numpy as np
import pandas as pd


arr = UtilsIO.changeCSVFileForLSTMCRF()

words = []
tags = []

for ingre in arr:
    for w, t in ingre:
        words.append(w)
        tags.append(t)

words.append("ENDPAD")
n_words = len(words);
n_tags = len(tags)+1;

word2ind = {word: index for index, word in enumerate(words)}
ind2word = {index: word for index, word in enumerate(words)}

label2ind = {label: (index + 1) for index, label in enumerate(tags)}
ind2label = {(index + 1): label for index, label in enumerate(tags)}

X = [[word2ind[w[0]] for w in s] for s in arr]
max_len = max([len(x) for x in X])

X = pad_sequences(maxlen=max_len, sequences=X, padding="post", value=n_words - 1)

y = [[label2ind[w[1]] for w in s] for s in arr]

y = pad_sequences(maxlen=max_len, sequences=y, padding="post")

y = [to_categorical(i, num_classes=n_tags) for i in y]


X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.1)

input = Input(shape=(max_len,))
model = Embedding(input_dim=n_words, output_dim=50, input_length=max_len)(input)
model = Dropout(0.1)(model)
model = Bidirectional(LSTM(units=100, return_sequences=True, recurrent_dropout=0.1))(model)
out = TimeDistributed(Dense(n_tags, activation="softmax"))(model)  # softmax output layer

model = Model(input, out)
model.compile(optimizer="rmsprop", loss="categorical_crossentropy", metrics=["accuracy"])



history = model.fit(X_tr, np.array(y_tr), batch_size=32, epochs=5,
                    validation_split=0.1, verbose=1)

i = 1927
p = model.predict(np.array([X_te[i]]))
p = np.argmax(p, axis=-1)
true = np.argmax(y_te[i], -1)
print("{:15}||{:5}||{}".format("Word", "True", "Pred"))
print(30 * "=")
for w, t, pred in zip(X_te[i], true, p[0]):
    if w != 0:
        print("{:15}: {:5} {}".format(words[w-1], tags[t], tags[pred]))
