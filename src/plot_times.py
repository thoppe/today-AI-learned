import glob, json, datetime, sqlite3
import pandas as pd
import pylab as plt
import seaborn as sns
import numpy as np


conn = sqlite3.connect("db/report.db",
                       detect_types=sqlite3.PARSE_DECLTYPES|
                       sqlite3.PARSE_COLNAMES)

cmd_search_bottom = '''SELECT 
wikipedia_url,top_TIL_title,top_upvotes,top_created_date
FROM crossref 
WHERE top_upvotes < 1000
AND   positive_search_result=1
GROUP BY wikipedia_url
'''

def add_time_buffer(T):
    T_min = T[T>20] - 24
    T_max = T[T<4]  + 24
    return np.hstack([T, T_min,T_max])
    
def add_labels():

    time_labels = ["midnight",
                   1,2,3,4,5,6,7,8,9,10,11]
    time_labels = [x if type(x)==str else "{} AM".format(x)
                   for x in time_labels]
    time_labels += ["noon",
                    1,2,3,4,5,6,7,8,9,10,11]
    time_labels = [x if type(x)==str else "{} PM".format(x)
                   for x in time_labels]
    plt.xticks(range(24),time_labels,rotation=90)
    plt.xlim(0,24)
    plt.ylim(0,0.07)

###################################################################

T = []
for url,title,votes,date in conn.execute(cmd_search_bottom):
    time = date.time()
    T.append( time.hour + time.minute/60. + time.second/3600. )

T = np.array(T)
T = add_time_buffer(T)


fig = plt.figure(figsize=(10,5))
sns.distplot(T,bins=(24+2*4))
plt.title("distribution of mined r/TIL posts with score < 1000")
add_labels()

f_png = "figures/bottom_TIL_time.png"
plt.tight_layout()
plt.savefig(f_png,bbox_inches='tight')

###################################################################

F_REDDIT = glob.glob("data/reddit/*.json")
F_REDDIT = F_REDDIT[:]

df = pd.DataFrame(
    index   = F_REDDIT,
    columns = ('time','score'))

for k,f in enumerate(F_REDDIT):
    print "Loading", f
    with open(f) as FIN:
        js = json.load(FIN)
        
    date = js["created_utc"]
    date = datetime.datetime.fromtimestamp(date)
    df.T[f]["score"] = js['score']

    time = date.time()
    df.T[f]["time"] = time.hour + time.minute/60. + time.second/3600.

# Add some wrapped time at ends to smooth out the histogram
T = df["time"].values
T = add_time_buffer(T)

fig = plt.figure(figsize=(10,5))
plt.title("distribution of r/TIL posts with score > 1000")
add_labels()
sns.distplot(T,bins=(24+2*4))
plt.tight_layout()

f_png = "figures/top_TIL_time.png"
plt.savefig(f_png,bbox_inches='tight')
plt.show()
