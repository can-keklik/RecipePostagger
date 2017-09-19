import PosTagger
import UtilsIO
import MisleaDataParser


def createGrapWithIndex(index):
    PosTagger.readData(index=index)
    UtilsIO.createPngFromDotFile("result" + str(index) + ".dot", "result" + str(index) + ".png")


def createGrapWithIndexForPaper(index):
    MisleaDataParser.readPaperData(index=index)
    #UtilsIO.createPngFromDotFile("papers/result" + str(index) + ".dot", "papers/result" + str(index) + ".png")


createGrapWithIndexForPaper(18)
#for i in range(4,33,1):
 #   createGrapWithIndexForPaper(i)
