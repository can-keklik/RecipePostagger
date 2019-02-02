import argparse
import MisleaDataParser
import numpy

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=numpy.int64, required=True)

    cnt = parser.parse_args()
    print("weqweqweqweqw", cnt.count)
    MisleaDataParser.createGrapWithIndexForPaper2(cnt.count)
