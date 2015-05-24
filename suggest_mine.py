import sqlite3, itertools, collections
import numpy as np
import os, string
from gensim.models.word2vec import Word2Vec
from sklearn.cross_validation import train_test_split
from sklearn.externals import joblib

'''
Use human-scored database to help figure out what might be good
to present next!
'''

f_features = "db/features.word2vec"
f_norm_scale = "db/scale.joblib"

conn = sqlite3.connect("db/report.db",
                       detect_types=sqlite3.PARSE_DECLTYPES|
                       sqlite3.PARSE_COLNAMES)

cmd_template = '''
DROP TABLE IF EXISTS suggestions;
CREATE TABLE IF NOT EXISTS suggestions 
(report_idx INTEGER PRIMARY KEY);
'''
conn.executescript(cmd_template)

HUMAN_LIMIT = 500
NEW_SUGGESTION_N = 10000
CORPUS_LIMIT = HUMAN_LIMIT*10

cmd_count_scored = "SELECT COUNT(*) FROM human_tracking"
total_scored = conn.execute(cmd_count_scored).next()[0]
total_scored = min(total_scored, HUMAN_LIMIT)

print "Found {} human scored entries".format(total_scored)

cmd_select_corpus_text = '''
SELECT wikipedia_title, wikipedia_text
FROM report as A
JOIN crossref AS B
ON A.report_idx==B.report_idx
LIMIT {}
'''.format(CORPUS_LIMIT)

cmd_select_human_scored = '''
SELECT B.wikipedia_title, B.wikipedia_text, A.status
FROM human_tracking AS A
JOIN report AS B
ON A.report_idx==B.report_idx
LIMIT {}
'''.format(HUMAN_LIMIT)

_STATUS_MAP = {
    "interesting":1,
    "mildly_interesting":2,
    "not_interesting":3,
    "media":4,
}

_INV_STATUS_MAP = {
    1:"interesting",
    2:"mildly_interesting",
    3:"not_interesting",
    4:"media",
}

_string_table = string.maketrans("","")
def process_text_item(text):
    result = text.lower()
    result = result.encode('ascii','ignore')
    result = result.translate(_string_table, string.punctuation)
    return result

def getWordVecs(text,dimension=100):
    vec = np.zeros(dimension).reshape((1, dimension))
    tokens = text.split()
    count  = 0.0
    
    for word in tokens:
        if word in features:
            vec   += features[word]
            count += 1

    if count:
        vec /= count
    else:
        vec[:] = 1.0

    return vec

def process_TRAINING_ITR(item):   
    title, text, status = item
    tokens = process_text_item(text+u' '+unicode(title))
    return getWordVecs(tokens), _STATUS_MAP[status]

def TRAINING_ITR():
    cursor = conn.execute(cmd_select_human_scored)
    return itertools.imap(process_TRAINING_ITR, cursor)

print "Loading model"
scalar = joblib.load(f_norm_scale)
features = Word2Vec.load(f_features)
dimension = 100

print "Building the training set"
X,Y = zip(*list(TRAINING_ITR()))
X = np.concatenate(X)

TTS = train_test_split
x_train, x_test, y_train, y_test = TTS(X, Y, test_size=0.17)

print "Scaling train vectors"
x_train = scalar.transform(x_train)

print "Scaling text vectors"
x_test = scalar.transform(x_test)

print "Training classifer"
from sklearn.ensemble import ExtraTreesClassifier as Classifier

clf = Classifier(n_estimators=200,n_jobs=8) # ExtraTrees
clf.fit(x_train, y_train)  

print 'Test Accuracy: %.3f'%clf.score(x_test, y_test)

y_test = np.array(y_test)
for n in _INV_STATUS_MAP.keys():
    idx = y_test==n
    try:
        score = clf.score(x_test[idx], y_test[idx])
    except:
        score = -1
    print 'Test Accuracy on {}: {:0.3f}'.format(_INV_STATUS_MAP[n],
                                                score)

    
print
print "Suggesting some new entries"

cmd_search_new = '''
SELECT A.report_idx,A.wikipedia_text,A.wikipedia_title
FROM report as A
JOIN crossref AS B
ON A.report_idx==B.report_idx
WHERE positive_search_result=0
AND A.report_idx NOT IN (SELECT A.report_idx FROM human_tracking)
ORDER BY RANDOM()
LIMIT {}
'''.format(NEW_SUGGESTION_N)

cursor = conn.execute(cmd_search_new)

VEC,RIDX = [],[]
for item in cursor:
    ridx, text, title = item
    tokens = process_text_item(text+u' '+unicode(title))
    vec = getWordVecs(tokens)
    RIDX.append(ridx)
    VEC.append(vec[0])

X = scalar.transform(VEC)
P = clf.predict(X)
print "Results of suggestions", collections.Counter(P)
interesting_ridx = np.array(RIDX)[P==1]


cmd_insert_suggestions = '''
INSERT INTO suggestions (report_idx) 
VALUES (?)
'''

values = [(x,) for x in interesting_ridx]
conn.executemany(cmd_insert_suggestions, values)
conn.commit()

print "Suggested {} new values,".format(len(values))
