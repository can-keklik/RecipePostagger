import UtilsIO
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from keras.layers import LSTM, Embedding, TimeDistributed, Bidirectional
from keras.models import Sequential
from keras.layers.core import Dense
from keras.models import model_from_json
import numpy as np
import utils
import keras.backend as K
import matplotlib.pyplot as plt


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


arr = UtilsIO.readIngredientData()

arr = arr[0:5000]
words = []
tags = []

for ingre in arr:
    for w, t in ingre:
        words.append(w)
        tags.append(t)


def trainAndSaveModel():
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

    X = [[word2idx[w[0]] for w in s] for s in arr]
    max_len = max([len(x) for x in X])
    X = pad_sequences(maxlen=max_len, sequences=X, padding="post", value=n_words - 1)

    y = [[tag2idx[w[1]] for w in s] for s in arr]

    y = pad_sequences(maxlen=max_len, sequences=y, padding="post")

    y = [to_categorical(i, num_classes=n_tags) for i in y]

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.1)
    model = Sequential()
    model.add(Embedding(input_dim=n_words, output_dim=50, input_length=max_len))
    model.add(Bidirectional(LSTM(units=100, return_sequences=True, recurrent_dropout=0.1)))
    model.add(TimeDistributed(Dense(n_tags, activation="softmax")))

    model.summary()

    model.compile(optimizer="rmsprop", loss="categorical_crossentropy",
                  metrics=['accuracy', f1_score, precision_val, recall_val])

    history = model.fit(np.array(X_tr), np.array(y_tr),validation_split=0.33, batch_size=32, epochs=6, verbose=1)

    print(history.history.keys())

    # summarize history for accuracy
    plt.title('Loss')
    plt.plot(history.history['loss'], label='train')
    plt.plot(history.history['val_loss'], label='test')
    plt.legend()
    plt.show();
    # summarize history for loss
    plt.title('Accuracy')
    plt.plot(history.history['acc'], label='train')
    plt.plot(history.history['val_acc'], label='test')
    plt.legend()
    plt.show();

    i = 50
    p = model.predict(np.array([X_te[i]]))
    p = np.argmax(p, axis=-1)
    print("{:15} ({:5}): {}".format("Word", "True", "Pred"))
    for w, pred in zip(X_te[i], p[0]):
        print("{:15}: {}".format(words[w], tags[pred]))
    scores = model.evaluate(np.array(X_te), np.array(y_te), verbose=1)
    print("%s: %.2f%%" % (model.metrics_names[1], scores[1] * 100))
    print("scores", scores)
    # serialize model to JSON
    model_json = model.to_json()
    with open("model1.json", "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights("model1.h5")
    print("Saved model to disk")


def loadTrainedModel():
    # load json and create model
    json_file = open('model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights("model.h5")
    print("Loaded model from disk")
    return loaded_model


# testData = ["1", "cup", "brown sugar","fillna"]

def predictIngredientTag(ingredient):
    display_input = utils.cleanUnicodeFractions(ingredient)

    tokens = utils.tokenizeWithoutPunctuation(display_input)
    word2idx = {w: i for i, w in enumerate(words)}
    X = [[word2idx[w[0]] for w in s] for s in arr]

    max_len = max([len(x) for x in X])
 #   print("maxle")
    x_testData = pad_sequences(sequences=[[word2idx.get(w, 0) for w in tokens]],
                               padding="post", value=0, maxlen=max_len)

    loadedModel = loadTrainedModel()
    p = loadedModel.predict(np.array([x_testData[0]]))
    p = np.argmax(p, axis=-1)
    retArr = []
    for w, pred in zip(tokens, p[0]):
        print("{:15}: {:5}".format(w, tags[pred]))
        retArr.append((w, tags[pred]))
    return retArr


def testmodel():
    trained_model = loadTrainedModel()
    arr = UtilsIO.readIngredientData()
    arr = arr[0:5000]
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

    X = [[word2idx[w[0]] for w in s] for s in arr]
    max_len = max([len(x) for x in X])
    X = pad_sequences(maxlen=max_len, sequences=X, padding="post", value=n_words - 1)

    y = [[tag2idx[w[1]] for w in s] for s in arr]

    y = pad_sequences(maxlen=max_len, sequences=y, padding="post")

    y = [to_categorical(i, num_classes=n_tags) for i in y]

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.1)
    scores = trained_model.evaluate(np.array(X_te), np.array(y_te), verbose=1)
    return scores


#print(predictIngredientTag("3/4 pound cooked chicken breast meat, very finely chopped"))
#trainAndSaveModel()
# print(testmodel())
trainAndSaveModel()