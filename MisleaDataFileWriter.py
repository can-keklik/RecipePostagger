import os

import MisleaDataParser


def writeData(index):
    (data, title) = MisleaDataParser.readData2(index=index)
    str_value = "title : " + title + "\n" + "\n"

    for i in xrange(len(data)):
        str_value = str_value + "SENT_ID :" + str(i) + "\n"
        for (word, tag, idx) in data[i]:
            str_value = str_value + str(tag) + " : " + str(word) + "\n"

        str_value = str_value + "\n"
    completeName = os.path.join(os.getcwd() + "/results/text_result/", title + ".txt")
    outFile = open(completeName, 'w')
    # print fileName
    outFile.truncate()
    outFile.write(str_value.encode('utf8'))
    outFile.close()


writeData(2)
