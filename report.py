import sqlite3, cPickle, itertools
from build_decoy_db import paragraph_iter
from sklearn.externals import joblib
import numpy as np

conn_decoy = sqlite3.connect("db/decoy.db")
f_wiki = "/media/travis/Seagate Expansion Drive/data_dump/wiki.db"
conn_wiki = sqlite3.connect(f_wiki, check_same_thread=False)

cmd_template = '''CREATE INDEX IF NOT 
EXISTS idx_title ON wiki (title)'''

print "Indexing titles"
conn_wiki.executescript(cmd_template)

cmd_select_positive_scores = '''
SELECT A.idx,
B.wikipedia_idx,B.wikipedia_title,B.paragraph_count 
FROM score AS A
JOIN decoy AS B ON A.idx=B.decoy_idx
WHERE score>0
LIMIT 20
'''

cmd_cross_reference = '''
SELECT wikipedia_idx 
'''

cmd_select_wiki = '''SELECT text FROM wiki WHERE title=?'''

def pprint_item(title, text):
    print u"# ---- {:s} ---".format(title)
    print u"# ---- {:s} ---".format(title)
    print text
    print


for item in conn_decoy.execute(cmd_select_positive_scores):
    idx,wiki_idx,title,para_n = item

    html = conn_wiki.execute(cmd_select_wiki, (title,)).next()[0]
    paragraphs = list(paragraph_iter(html))
    title = unicode(title)

    if paragraphs:
        pprint_item(title, paragraphs[para_n])



