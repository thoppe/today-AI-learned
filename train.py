import sqlite3, itertools
import numpy as np
from gensim.models.word2vec import Word2Vec

from sklearn.cross_validation import train_test_split
from sklearn.externals import joblib

from sklearn import preprocessing
import src.build_features as feat

#FLAG_BUILD_DECOY_LIST = True
FLAG_BUILD_DECOY_LIST = False

# When training, how big of a decoy set to use
_DECOY_PROPORTION = 5

conn_decoy = feat.conn_decoy
conn_train = feat.conn_train

f_clf   = "db/clf.joblib"
f_norm_scale = "db/scale.joblib"

total_samples = feat.count_WIKI_corpus()

def query_skip_decoys():

    cmd_select = '''SELECT tokens,weights FROM decoy AS A
    JOIN skip_decoy_query AS B ON A.decoy_idx=B.decoy_idx
    '''
    cursor = conn_decoy.execute(cmd_select)
    for text,weight_str in cursor:
        # Load the entropy weight
        w = np.fromstring(weight_str[1:-1],sep=',')
        yield text, w
            

def build_skip_query(skip_n):
    cmd_template = '''
    DROP TABLE IF EXISTS skip_decoy_query;
    CREATE TABLE skip_decoy_query (decoy_idx INTEGER PRIMARY KEY);'''
    conn_decoy.executescript(cmd_template)
    
    cmd_find = '''
    SELECT decoy_idx, wikipedia_title 
    FROM decoy WHERE decoy_idx%{}==0'''.format(skip_n)
    cmd_insert = '''INSERT INTO skip_decoy_query (decoy_idx) VALUES (?)'''
    cursor = conn_decoy.execute(cmd_find)
    
    for idx,title in cursor:
        print idx, title
        conn_decoy.execute(cmd_insert, (idx,))

    conn_decoy.commit()
    
def getWordVecs(text,weight,features,dimension):

    # The vector is the entropy-weighted average of each word
    vec = np.zeros(dimension).reshape((1, dimension))

    tokens = text.split()
    count  = 0.0
    
    for single_entropy,word in zip(weight,tokens):
        if word in features:
            vec   += single_entropy*features[word]
            count += single_entropy
            
    vec /= count
    if np.isnan(vec).any():
        vec[:] = 1.0

    return vec


def train_model():

    TIL_n     = feat.count_TIL_corpus()
    decoy_n   = TIL_n*_DECOY_PROPORTION
    FP_n      = feat.count_TIL_false_pos()

    wiki_n    = feat.count_WIKI_corpus()
    skip_wiki_n =  wiki_n // decoy_n

    # Keep the number of false positives in about the same Order-of-Mag
    skip_FP  = FP_n // TIL_n
    print "Skipping every {} value in FP".format(skip_FP)

    if FLAG_BUILD_DECOY_LIST:
        build_skip_query(skip_wiki_n)

    print "Loading features"
    features = Word2Vec.load(feat.f_features)
    dimension = 100 # default dimension
  

    ITR_decoy = query_skip_decoys()

    print "Building training set"
    ITR_train = list(feat.TIL_full_corpus_iter())

    print "Building the false positive set"
    ITR_FP    = list(feat.TIL_false_pos_iter(skip_FP))

    print "Building corpus iter"
    ITR = feat.chainer(ITR_train, ITR_FP, ITR_decoy)
    ITR = list(ITR)
    
    Y = np.zeros(len(ITR))
    Y[:TIL_n] = 1.0

    TTS = train_test_split
    x_train, x_test, y_train, y_test = TTS(ITR, Y, test_size=0.2)

    print "Proportion of answers {}/{}".format(y_train.sum(), y_test.sum())

    print "Calculating the wordVecs for train"
    vec_train = np.concatenate([getWordVecs(text,weight,features,dimension)
                                for text,weight in x_train])
        
    print "Building the scalar"
    scaler = preprocessing.StandardScaler().fit(vec_train)

    print "Saving the scaler"
    joblib.dump(scaler, f_norm_scale)

    print "Scaling train vectors"
    vec_train = scaler.transform(vec_train)

    print "Calculating the wordVecs for test"
    vec_test = np.concatenate([getWordVecs(text,weight,features,dimension)
                               for text,weight in x_test])

    print "Scaling test vectors"
    vec_test = scaler.transform(vec_test)

    print "Train size/TP in sample", vec_train.shape, (y_train==1).sum()
    print "Test  size/TP in sample", vec_test.shape, (y_test==1).sum()
    print "Training classifer"

    #from sklearn.linear_model import SGDClassifier as Classifier
    #from sklearn.linear_model import LogisticRegression as Classifier
    #from sklearn.linear_model import BayesianRidge as Classifier
    #from sklearn.naive_bayes import BernoulliNB as Classifier
    #from sklearn.naive_bayes import GaussianNB as Classifier
    #from sklearn.naive_bayes import GaussianNB as Classifier
    #from sklearn.ensemble import RandomForestClassifier as Classifier
    from sklearn.ensemble import ExtraTreesClassifier as Classifier
    
    # This seems to be the best... but high FP rate
    #from sklearn.naive_bayes import BernoulliNB as Classifier    
 
    #clf = Classifier(loss='log', penalty='l1',verbose=2) # SGD
    #clf =  Classifier(C=2500,verbose=2) # LogisiticRegression
    #clf =  Classifier() # Naive Bayes
    clf = Classifier(n_estimators=200,n_jobs=8) # ExtraTrees
    
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
    train_model()
