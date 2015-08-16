import sqlite3, cPickle, itertools
from build_decoy_db import paragraph_iter
from sklearn.externals import joblib
import numpy as np
import urllib
from parsing import tokenize

conn_report = sqlite3.connect("db/report.db")

cmd_template = '''
DROP TABLE IF EXISTS report;
CREATE TABLE IF NOT EXISTS report (
   report_idx INTEGER PRIMARY KEY AUTOINCREMENT,
   wikipedia_title STRING,
   wikipedia_text STRING,
   tokens STRING
);
'''
conn_report.executescript(cmd_template)

cmd_insert_into_report = '''
INSERT INTO report 
(wikipedia_title, wikipedia_text, tokens)
VALUES (?,?,?)
'''

conn_decoy = sqlite3.connect("db/decoy.db")
f_wiki = "/media/travis/Seagate Expansion Drive/data_dump/wiki.db"
conn_wiki = sqlite3.connect(f_wiki, check_same_thread=False)

cmd_index = '''CREATE INDEX IF NOT 
EXISTS idx_title ON wiki (title)'''

print "Indexing titles"
conn_wiki.executescript(cmd_index)

cmd_select_positive_scores = '''
SELECT A.idx,
B.wikipedia_idx,B.wikipedia_title,B.paragraph_count 
FROM score AS A
JOIN decoy AS B ON A.idx=B.decoy_idx
WHERE score>0
--LIMIT 5
'''

cmd_select_wiki = '''SELECT text FROM wiki WHERE title=?'''

def pprint_item(title, text):
    base_url = "http://en.wikipedia.org/w/index.php?title={}"

    try:
        url = base_url.format(urllib.quote(title))
        print u"# [{:s}]({:s})".format(title,url)
        print text.encode('utf-8')
        print
    except:
        pass


for item in conn_decoy.execute(cmd_select_positive_scores):
    idx,wiki_idx,title,para_n = item

    html = conn_wiki.execute(cmd_select_wiki, (title,)).next()[0]
    paragraphs = list(paragraph_iter(html))
    title = unicode(title)

    if paragraphs:
        print title
        text = paragraphs[para_n]
        tokens = u' '.join(tokenize(text))

        conn_report.execute(cmd_insert_into_report,
                            (title, text, tokens))

conn_report.commit()



