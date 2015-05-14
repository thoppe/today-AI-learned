# -*- coding: utf-8 -*-
import requests_cache
requests_cache.install_cache('demo_cache')

import datetime, time
import sqlite3, itertools, subprocess
import praw

reddit = praw.Reddit(user_agent='crossref_TIL')
conn = sqlite3.connect("db/report.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
cmd_template = '''
--DROP TABLE IF EXISTS crossref;
CREATE TABLE IF NOT EXISTS crossref (
    report_idx INTEGER PRIMARY KEY,
    wikipedia_url STRING,
    positive_search_result BOOL,
    top_created_date TIMESTAMP,
    top_upvotes INTEGER,
    top_TIL_title STRING,
    top_num_comments INTEGER,
    top_reddit_id STRING
);
INSERT OR IGNORE INTO crossref (report_idx)
SELECT report_idx FROM report;
'''
conn.executescript(cmd_template)

cmd_search = '''SELECT 
A.report_idx, wikipedia_title, wikipedia_text, tokens
FROM report AS A
JOIN crossref AS B
ON A.report_idx==B.report_idx
WHERE B.positive_search_result IS NULL
ORDER BY A.report_idx
'''

cursor = conn.execute(cmd_search)
base_url = u"https://en.wikipedia.org/wiki/{}"

for (ridx, title, text, tokens) in cursor:
    print "Starting", title
    #title = u"2004 Harvard–Yale prank"
    
    title   = unicode(title)
    
    w_title = subprocess.check_output([u"python3",
                                       u"src/mediawiki_title.py",
                                       u'"{}"'.format(title)])
    w_title = w_title.strip()[1:-1].decode('utf-8')

    search_url = base_url.format(w_title)

    query = u"url:{}".format(search_url)
    search = reddit.search(query,subreddit="todayilearned",
                           sort="top",period="all")

    try:
        post = search.next()
        was_found = True
    except StopIteration:
        # No post was found!
        was_found = False

    cmd_insert_none = '''
    UPDATE crossref SET
    wikipedia_url=?,
    positive_search_result=0
    WHERE report_idx = (?)'''

    cmd_insert_found = '''
    UPDATE crossref SET
    wikipedia_url=?,
    positive_search_result=1,
    top_upvotes=?,
    top_TIL_title=?,
    top_num_comments=?,
    top_reddit_id=?,
    top_created_date=?
    WHERE report_idx = (?)'''

    cols = (search_url,)

    if not was_found:
        conn.execute(cmd_insert_none, cols+(ridx,))
        print " -- No results found!"
    else:
        created_date = post.created_utc
        created_date = datetime.datetime.fromtimestamp(created_date)
        
        cols += (post.ups,
                 post.title,
                 post.num_comments,
                 post.name,
                 created_date,
                 ridx)

        conn.execute(cmd_insert_found, cols)
        print " --", post.title, ridx

    conn.commit()

