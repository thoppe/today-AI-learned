import sqlite3, cPickle, itertools
from src.parsing import tokenize
import numpy as np
from gensim.models.word2vec import Word2Vec
from sklearn.cross_validation import train_test_split
from sklearn.externals import joblib

from sklearn import preprocessing
 

# Addtional stop-words gleaned from trial-and-error
#extra_stop_words = ["would","us","could","get","000","amp","go","ad","uk"
#                    "mt","ny","ii","tv","1100ad"]

# Number of entries to skip when training,
# if not used leads to massive training time
#_SKIP_DECOY = 1
#_SQL_LIMIT  = 10**10

# When training, how big of a decoy set to use
_DECOY_PROPORTION = 5

conn_decoy = sqlite3.connect("db/decoy.db")
conn_train = sqlite3.connect("db/training.db")

f_model = "db/model.word2vec"
f_clf   = "db/clf.joblib"
f_norm_scale = "db/scale.joblib"

def decoy_corpus_iter(offset=0,skip=1,limit=10**10):
    cmd_select = "SELECT wikitext FROM decoy LIMIT {}".format(limit)
    cursor = conn_decoy.execute(cmd_select)
    
    for _ in xrange(offset):
        cursor.next()
        
    for k,(text,) in enumerate(cursor):
        if k and k%10000==0:
            print "Loaded {:0.4f}% samples".format(k/float(total_samples))
        if k%skip==0:
            yield unicode(text).split()

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

def count_TIL_false_pos():
    cmd_count = "SELECT MAX(_ROWID_) FROM false_positives LIMIT 1"
    return conn_train.execute(cmd_count).next()[0]

def count_WIKI_corpus():
    cmd_count = "SELECT MAX(_ROWID_) FROM decoy LIMIT 1"
    return conn_decoy.execute(cmd_count).next()[0]

total_samples = count_WIKI_corpus()

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

##############################################################################

def build_features():
    print "Calculating feature vector"
    ITR_decoy = decoy_corpus_iter(offset=0,
                                  skip=_SKIP_DECOY,
                                  limit=_SQL_LIMIT)
    ITR_train = TIL_corpus_iter()
    ITR = chainer(ITR_train, ITR_decoy)

    model = Word2Vec(workers=8)
    model.build_vocab(ITR)

    # Rebuild the iterators
    ITR_decoy = decoy_corpus_iter(offset=0,
                                  skip=_SKIP_DECOY,
                                  limit=_SQL_LIMIT)   
    ITR_train = TIL_corpus_iter()
    ITR = chainer(ITR_train, ITR_decoy)
    model.train(ITR)

    print "Reducing the model"
    model.init_sims(replace=True)

    print "Saving updated model"
    model.save(f_model)

###################################################################

def TIL_full_corpus_iter():
    cmd_select = "SELECT wikitext,weights FROM training"

    cursor = conn_train.execute(cmd_select)
    for (text,weight_str) in cursor.fetchall():
        # Load the entropy weight
        w = np.fromstring(weight_str[1:-1],sep=',')
        yield text, w

def TIL_false_pos_iter():
    cmd_select = "SELECT wikitext,weights FROM false_positives"

    cursor = conn_train.execute(cmd_select)
    for (text,weight_str) in cursor.fetchall():
        # Load the entropy weight
        w = np.fromstring(weight_str[1:-1],sep=',')
        yield text, w  
        

def query_random_decoys(size):
    IDX_SET = np.random.randint(0, count_WIKI_corpus()-1, size=size)

    def grouper(iterable, n):
        return itertools.izip_longest(*[iter(iterable)]*n)

    cmd_select = "SELECT wikitext,weights FROM decoy WHERE idx IN {}"
    chunk_size = 100
    for block in grouper(IDX_SET, chunk_size):
        block = (x for x in block if x is not None)
        cmd = cmd_select.format(tuple(block))
        cursor = conn_decoy.execute(cmd)
        for text,weight_str in cursor.fetchall():

            # Load the entropy weight
            w = np.fromstring(weight_str[1:-1],sep=',')
            yield text, w

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


def train_model():

    print "Loading model"
    model = Word2Vec.load(f_model)
    dimension = 100 # default dimension

    print "Building training set"
    TIL_n     = count_TIL_corpus()
    decoy_n   = TIL_n*_DECOY_PROPORTION
    FP_n      = count_TIL_false_pos()

    print "Building full corpus iter"    
    ITR_train = TIL_full_corpus_iter()
    ITR_decoy = query_random_decoys(decoy_n)
    ITR_FP    = TIL_false_pos_iter()

    ITR = chainer(ITR_train, ITR_FP, ITR_decoy)
    Y = np.zeros(TIL_n+decoy_n+FP_n)
    Y[:TIL_n] = 1.0

    TTS = train_test_split
    x_train, x_test, y_train, y_test = TTS(list(ITR), Y, test_size=0.2)

    print "Proportion of answers {}/{}".format(y_train.sum(), y_test.sum())

    # Train the scaler on the test data
    vec_test = np.concatenate([getWordVecs(text,weight,model,dimension)
                               for text,weight in x_test])
    
    scaler = preprocessing.StandardScaler().fit(vec_test)
    print "Saving the scaler"
    joblib.dump(scaler, f_norm_scale)


    vec_test = scaler.transform(vec_test)

    # Build the scaled train vectors
    vec_train = np.concatenate([getWordVecs(text,weight,model,dimension)
                                for text,weight in x_train])
    
    vec_train = scaler.transform(vec_train)
        
    print vec_test.shape
    print vec_train.shape

    print "Training classifer"

    #from sklearn.linear_model import SGDClassifier as Classifier
    #from sklearn.linear_model import LogisticRegression as Classifier
    #from sklearn.linear_model import BayesianRidge as Classifier
    #from sklearn.naive_bayes import BernoulliNB as Classifier
    #from sklearn.naive_bayes import GaussianNB as Classifier

    # This seems to be the best... but high FP rate
    from sklearn.naive_bayes import BernoulliNB as Classifier    
 
    #clf = Classifier(loss='log', penalty='l1',verbose=2) # SGD
    #clf =  Classifier(C=2500,verbose=2) # LogisiticRegression
    clf =  Classifier() # Naive Bayes
    
    clf.fit(vec_train, y_train)  

    print 'Test Accuracy: %.3f'%clf.score(vec_test, y_test)

    idx_TP = np.array(y_test) > 0
    vec_TP = np.array(vec_test)[idx_TP]
    y_TP   = np.array(y_test)[idx_TP]
    print 'Test Accuracy on TP: %.3f'%clf.score(vec_TP, y_TP)

    vec_FP = np.array(vec_test)[~idx_TP]
    y_FP   = np.array(y_test)[~idx_TP]
    print 'Test Accuracy on FP: %.3f'%clf.score(vec_FP, y_FP)

    print "Saving the classifer"
    joblib.dump(clf, f_clf)

    #Create ROC curve
    from sklearn.metrics import roc_curve, auc
    import matplotlib.pyplot as plt

    pred_probas = clf.predict_proba(vec_test)[:,1]
    fpr,tpr,_ = roc_curve(y_test, pred_probas)
    roc_auc = auc(fpr,tpr)
    plt.plot(fpr,tpr,label='area = %.2f' %roc_auc)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.legend(loc='lower right')
    plt.show()

if __name__ == "__main__":
    #build_features()
    train_model()
