
import gensim as gensim
# todo inorder to run this code first download GoogleNews-vectors-negative300.bin from Internet...
model = gensim.models.Word2Vec.load_word2vec_format('./tmp/GoogleNews-vectors-negative300.bin', binary=True)
model.init_sims(replace=True)
model.save('SmallerFile')