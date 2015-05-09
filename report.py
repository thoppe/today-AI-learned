import sqlite3, cPickle, itertools
from build_decoy_db import paragraph_iter
from sklearn.externals import joblib
import numpy as np


conn_decoy = sqlite3.connect("db/decoy.db")
f_wiki = "/media/travis/Seagate Expansion Drive/data_dump/wiki.db"
conn_wiki = sqlite3.connect(f_wiki, check_same_thread=False)

cmd_template = '''CREATE INDEX IF NOT EXISTS idx_title ON wiki (title);'''
print "Indexing titles"
conn_wiki.executescript(cmd_template)

cmd_select_top_scores = '''
SELECT A.idx,B.wiki_title,B.paragraph_count FROM score AS A
JOIN decoy AS B ON A.idx=B.idx
WHERE score>0
LIMIT 2000
'''

cmd_find_scored = '''
SELECT idx FROM score WHERE score>0 LIMIT 30'''

cmd_select_wiki = '''SELECT text FROM wiki WHERE title=?'''

def pprint_item(title, text):
    print u"---- {:s} ---".format(title)
    print text


for item in conn_decoy.execute(cmd_select_top_scores):
    idx,title,para_n = item
    html = conn_wiki.execute(cmd_select_wiki, (title,)).next()[0]
    paragraphs = list(paragraph_iter(html))

    if paragraphs:
        print paragraphs, para_n
        print html
        pprint_item(title, paragraphs[para_n])

exit()


'''
f_TFID  = "db/classifer.joblib"
f_model = "db/model/model.joblib"
clf = joblib.load(f_model)
features = joblib.load(f_TFID)

#weight = clf.feature_importances_
weight = clf.coef_[0]
names  = features.get_feature_names()
print weight
print weight.shape
print len(names)
#import pylab as plt
#import seaborn as sns
n = len(weight)
idx = np.argsort(weight)[::-1]

for i in idx[:50]:
    print weight[i], names[i]

exit()
'''




# Index for fast lookups
cmd_template = '''CREATE INDEX IF NOT EXISTS idx_score ON score (score);'''
print "Indexing score"
conn_decoy.executescript(cmd_template)



cursor = conn_decoy.execute(cmd_select_top_scores)

for (score,title,condensed_text,para_n) in cursor:
    html = conn_wiki.execute(cmd_select_wiki, (title,)).next()[0]
    paragraphs = list(paragraph_iter(html))
    text = paragraphs[para_n]
    print u"---- {:s} ({:0.2f}) ---".format(title,score)
    print text
    '''
    print condensed_text
    print para_n
    print
    for n,x in enumerate(paragraphs):
        print n,x

    exit()
    '''

