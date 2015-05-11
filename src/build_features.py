import sqlite3, itertools
from gensim.models.word2vec import Word2Vec
from parsing import tokenize
import numpy as np

#help(Word2Vec)
#exit()

# Number of entries to skip when training,
# if not used leads to massive training time
_SKIP_DECOY = 1
_SQL_LIMIT  = 10**10

conn_decoy = sqlite3.connect("db/decoy.db")
conn_train = sqlite3.connect("db/training.db")

f_features = "db/features.word2vec"

####################################################################

def decoy_corpus_iter(offset=0,skip=1,limit=10**10):
    cmd_select = "SELECT tokens FROM decoy LIMIT {}".format(limit)
    cursor = conn_decoy.execute(cmd_select)
    
    for _ in xrange(offset):
        cursor.next()
        
    for k,(text,) in enumerate(cursor):
        if k and k%10000==0:
            num = k/float(total_samples)
            print "Loaded {:0.4f}% samples".format(num)
        if k%skip==0:
            yield unicode(text).split()

#################################################################

def TIL_corpus_iter(skip=1):
    cmd_select = "SELECT unprocessed_wikitext FROM training"

    cursor = conn_train.execute(cmd_select)
    for k,(text,) in enumerate(cursor):
        if k%skip==0:
            text = unicode(text)
            text = ' '.join(set(tokenize(text)))
            yield text.split()

def count_TIL_corpus():
    cmd_count = "SELECT MAX(_ROWID_) FROM training LIMIT 1"
    return conn_train.execute(cmd_count).next()[0]


def TIL_full_corpus_iter():
    cmd_select = "SELECT tokens,weights FROM training"

    cursor = conn_train.execute(cmd_select)
    for (text,weight_str) in cursor.fetchall():
        # Load the entropy weight
        w = np.fromstring(weight_str[1:-1],sep=',')
        yield text, w

def TIL_false_pos_iter(skip_count=None):
    if not skip_count:
        cmd_select = "SELECT tokens,weights FROM false_positives"
    else:
        cmd_select = '''
        SELECT tokens,weights FROM false_positives
        WHERE idx%{}==0
        '''.format(skip_count)
        
    cursor = conn_train.execute(cmd_select)
    for (text,weight_str) in cursor:
        # Load the entropy weight
        w = np.fromstring(weight_str[1:-1],sep=',')
        yield text, w

def count_TIL_false_pos():
    cmd_count = "SELECT MAX(_ROWID_) FROM false_positives LIMIT 1"
    return conn_train.execute(cmd_count).next()[0]

def count_WIKI_corpus():
    cmd_count = "SELECT MAX(_ROWID_) FROM decoy LIMIT 1"
    return conn_decoy.execute(cmd_count).next()[0]

total_samples = count_WIKI_corpus()

#################################################################

class chainer(object):
    ''' Chains iterators together and keeps track of their size '''
    def __init__(self,*args):
        self.ITRS  = args
        self.counts = []
    def __iter__(self):
        for itr in self.ITRS:
            count = 0
            for item in itr:
                count += 1
                yield item
            self.counts.append(count)
    def get_sizes(self):
        return self.counts

#################################################################


def build_features():
    print "Calculating feature vector"
    ITR_decoy = decoy_corpus_iter(offset=0,
                                  skip=_SKIP_DECOY,
                                  limit=_SQL_LIMIT)
    ITR_train = TIL_corpus_iter()
    ITR = chainer(ITR_train, ITR_decoy)

    features = Word2Vec(workers=8, min_count=30)
    features.build_vocab(ITR)

    # Rebuild the iterators
    ITR_decoy = decoy_corpus_iter(offset=0,
                                  skip=_SKIP_DECOY,
                                  limit=_SQL_LIMIT)   
    ITR_train = TIL_corpus_iter()
    ITR = chainer(ITR_train, ITR_decoy)
    features.train(ITR)

    print "Reducing the features"
    features.init_sims(replace=True)

    print "Saving updated features"
    features.save(f_features)

if __name__ == "__main__":
    build_features()
