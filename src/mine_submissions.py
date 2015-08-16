import sqlite3, itertools, datetime
import numpy as np
import webbrowser,os,textwrap
from parsing import tokenize, frequency_table

'''
Small interactive program to help a human label the prospective submissions.
'''


conn = sqlite3.connect("db/report.db",
                       detect_types=sqlite3.PARSE_DECLTYPES|
                       sqlite3.PARSE_COLNAMES)

# Reads a single keystroke (why so hard?!)
def _find_getch():
    try:
        import termios
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return msvcrt.getch

    # POSIX system. Create and return a getch that manipulates the tty.
    import sys, tty
    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch
getch = _find_getch()

# Keep track of what we've seen before

cmd_template = '''
--DROP TABLE human_tracking;
CREATE TABLE IF NOT EXISTS human_tracking(
    report_idx INTEGER PRIMARY KEY,
    status STRING,
    submitted_status BOOL DEFAULT 0,
    date_classified TIMESTAMP
);
CREATE TABLE IF NOT EXISTS suggestions 
(report_idx INTEGER PRIMARY KEY);
'''
conn.executescript(cmd_template)

cmd_mark_tracking = '''
INSERT INTO human_tracking (report_idx, status,date_classified)
VALUES (?,?,?)
'''

cmd_search_new = '''
SELECT A.report_idx,
wikipedia_title, wikipedia_text,wikipedia_url 
FROM report as A
JOIN crossref AS B
ON A.report_idx==B.report_idx
WHERE positive_search_result=0
AND A.report_idx NOT IN (SELECT report_idx FROM human_tracking)
ORDER BY RANDOM()
LIMIT 1
'''

cmd_search_suggestions = '''
SELECT report_idx,
wikipedia_title, wikipedia_text, wikipedia_url
FROM suggestions as A
NATURAL JOIN report AS B
NATURAL JOIN crossref AS C
LIMIT 1
'''

cmd_remove_suggestion = '''
DELETE FROM suggestions
WHERE report_idx=?
'''


def get_remaining_suggestions():
    cursor = conn.execute("SELECT COUNT(*) FROM suggestions")
    return cursor.next()[0]

fmt = u'''\t\t\t\t=== {} ===
{}
{}

1. Interesting!
2. Mildly interesting...
3. Not interesting :(
4. Book/Film/Movie

s  SKIP!
x  EXIT PROGRAM
d  DUMP Interesting
'''

response = {
    "1":"interesting",
    "2":"mildly_interesting",
    "3":"not_interesting",
    "4":"media",
    "x":None,
    "s":None,
    "d":None,
}

while True:

    os.system("clear")
    SUGGESTION_FLAG = False

    if not get_remaining_suggestions():
        cursor = conn.execute(cmd_search_new)
    else:
        SUGGESTION_FLAG = True
        cursor = conn.execute(cmd_search_suggestions)

    ridx,title,text,url = cursor.next()
    cursor.close()

    # Let the user know this is a suggested flag
    if SUGGESTION_FLAG:
        title = u"(S) {}".format(title)

    # Make this nice to read on the terminal
    text = textwrap.fill(text, 80)

    key = "."
    while key not in response.keys():
        webbrowser.open(url,new=0)
        
        print fmt.format(title,url,text)
        key = getch()

    status = response[key]

    if key.lower() == "x":
        exit()

    if key.lower() == "d":
        break    

    if key.lower() != "s":
        time = datetime.datetime.now()
        conn.execute(cmd_mark_tracking, (ridx,status,time))
        conn.commit()

    # Even if skipped, remove the suggestion
    if SUGGESTION_FLAG:
        conn.execute(cmd_remove_suggestion,(ridx,))
        conn.commit()


        


cmd_search_top = '''
SELECT 
A.wikipedia_title, B.date_classified, A.wikipedia_text
FROM report as A
JOIN human_tracking AS B
ON A.report_idx==B.report_idx
WHERE B.status=="interesting"
ORDER BY date_classified
'''


if key.lower() == "d":
    cursor = conn.execute(cmd_search_top)
    for title,date,text in cursor:
        print title,'\t', date,'\t',text
        
