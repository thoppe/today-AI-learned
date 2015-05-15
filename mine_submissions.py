import sqlite3, itertools, datetime
import numpy as np
import webbrowser,os

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


conn = sqlite3.connect("db/report.db",
                       detect_types=sqlite3.PARSE_DECLTYPES|
                       sqlite3.PARSE_COLNAMES)

# Keep track of what we've seen before

cmd_template = '''
--DROP TABLE human_tracking;
CREATE TABLE IF NOT EXISTS human_tracking(
    report_idx INTEGER PRIMARY KEY,
    status STRING,
    submitted_status BOOL DEFAULT 0
);'''
conn.executescript(cmd_template)

cmd_mark_tracking = '''
INSERT INTO human_tracking (report_idx, status)
VALUES (?,?)
'''


cmd_search_new = '''
SELECT A.report_idx,
wikipedia_title, wikipedia_text,wikipedia_url 
FROM report as A
JOIN crossref AS B
ON A.report_idx==B.report_idx
WHERE positive_search_result=0
ORDER BY RANDOM()
LIMIT 1
'''

fmt = u'''\t\t\t\t=== {} ===
{}
{}

1. Interesting!
2. Mildly interesting...
3. Not interesting :(
4. Book/Film/Movie

s  SKIP!
x  EXIT PROGRAM
'''

response = {
    "1":"interesting",
    "2":"mildly_interesting",
    "3":"not_interesting",
    "4":"media",
    "x":None,
    "s":None,
}

while True:
    os.system("clear")
    cursor = conn.execute(cmd_search_new)
    ridx,title,text,url = cursor.next()
    cursor.close()

    key = "."
    while key not in response.keys():
        webbrowser.get().open(url,new=0)
        print fmt.format(title,url,text)
        key = getch()

    status = response[key]

    if key.lower() == "x":
        exit()

    if key.lower() != "s":
        conn.execute(cmd_mark_tracking, (ridx,status))
        conn.commit()
    
