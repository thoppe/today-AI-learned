import sqlite3, itertools
import numpy as np
from sklearn.externals import joblib
from gensim.models.word2vec import Word2Vec
import build_features as feat

conn_decoy = sqlite3.connect("db/decoy.db")

f_features = "db/features.word2vec"
f_clf   = "db/clf.joblib"
f_norm_scale = "db/scale.joblib"

scalar = joblib.load(f_norm_scale)
clf = joblib.load(f_clf)

print "Loading model"
features = Word2Vec.load(f_features)
dimension = 100

# Create the score table
cmd_template = '''
DROP TABLE IF EXISTS score;
CREATE TABLE IF NOT EXISTS score (
    idx INTEGER PRIMARY KEY NOT NULL,
    score FLOAT DEFAULT NULL
); 

INSERT INTO score (idx)
SELECT decoy_idx FROM decoy;
'''
#print "Templating"
#conn_decoy.executescript(cmd_template)

total_samples = feat.count_WIKI_corpus()

cmd_check_remaining = '''SELECT COUNT(*) FROM score WHERE score IS NULL'''
score_remaining = conn_decoy.execute(cmd_check_remaining).next()
print "There are {} left to score".format(score_remaining)

def getWordVecs(text,weight,model,dimension):

    # The vector is the entropy-weighted average of each word
    vec = np.zeros(dimension).reshape((1, dimension))

    tokens = text.split()
    count  = 0.0
    
    for single_entropy,word in zip(weight,tokens):
        if word in model:
            vec   += single_entropy*model[word]
            count += single_entropy
            
    vec /= count
    if np.isnan(vec).any():
        vec[:] = 1.0

    return vec


def decoy_vec_iter():

    # Select the values we haven't seen before
    cmd_select = '''
    SELECT A.decoy_idx, A.tokens,A.weights FROM decoy AS A
    JOIN score AS B ON A.decoy_idx=B.idx
    WHERE B.score IS NULL
    '''
    cursor = conn_decoy.execute(cmd_select)
    for idx,text,w_str in cursor:
        w = np.fromstring(w_str[1:-1],sep=',')
        vec = getWordVecs(text,w,features,dimension)
        
        yield idx, scalar.transform(vec)

def grouper(ITR, size):
    data = []
    for item in ITR:
        data.append(item)
        if len(data)==size:
            yield data
            data = []
    yield data

def predict_block(item):

    IDX, VEC = zip(*item)
    VEC = np.vstack(VEC)

    score = clf.predict(VEC).astype(int)
    return score,IDX

cmd_update = '''UPDATE score
SET score=?
WHERE idx=?
'''


DATA = grouper(decoy_vec_iter(), 10000)
ITR = itertools.imap(predict_block, DATA)

#import multiprocessing
#P = multiprocessing.Pool(4)
#ITR = P.imap(predict_block, DATA)

for k,(score,IDX) in enumerate(ITR):
    print k, sum(score)
    conn_decoy.executemany(cmd_update, zip(score,IDX))

    if k and k%10==0:
        print "Commiting"
        conn_decoy.commit()

conn_decoy.commit()


'''
def result_ITR():
    print "Starting prediction"
    for k,(idx,vec) in enumerate(ITR):
        
        score = clf.predict(vec)[0]
        if score:
            print k, idx, score
                   
        # Round to int
        score = int(score)

        yield score,idx

conn_decoy.executemany(cmd_update, result_ITR())
conn_decoy.commit()
'''
