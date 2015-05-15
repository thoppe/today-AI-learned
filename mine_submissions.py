import sqlite3, itertools, datetime
import numpy as np

conn = sqlite3.connect("db/report.db",
                       detect_types=sqlite3.PARSE_DECLTYPES|
                       sqlite3.PARSE_COLNAMES)
cmd_search_new = '''
SELECT wikipedia_title, wikipedia_text,wikipedia_url 
FROM report as A
JOIN crossref AS B 
ON A.report_idx==B.report_idx
WHERE positive_search_result=0
ORDER BY RANDOM()
LIMIT 50
'''

fmt = u'''=== {} ===
{}
{}
'''
for title,text,url in conn.execute(cmd_search_new):
    print fmt.format(title,url,text)
    
