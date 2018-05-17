import os
import threading

import PapersParsedRecipeGeneration

filenames = os.listdir(PapersParsedRecipeGeneration.RESULTS_URL)
for filename in filenames:
    print(filename)
    thread = threading.Thread(target=PapersParsedRecipeGeneration.parseRecipeDataFromFile(filenames[2]))
    thread.start()
