import PosTagger
import UtilsIO


def createGrapWithIndex(index):
    PosTagger.readData(index=index)
    UtilsIO.createPngFromDotFile("result" + str(index) + ".dot", "result" + str(index) + ".png")


createGrapWithIndex(20)
