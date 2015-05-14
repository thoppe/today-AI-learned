import glob, json, datetime
import pandas as pd
import pylab as plt
import seaborn as sns
import numpy as np

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

# Add some fake time at ends to smooth out the histogram
T = df["time"].values
T_min = T[T>20] - 24
T_max = T[T<4]  + 24
T = np.hstack([T, T_min,T_max])

time_labels = ["midnight",
               1,2,3,4,5,6,7,8,9,10,11]
time_labels = [x if type(x)==str else "{} AM".format(x)
               for x in time_labels]
time_labels += ["noon",
                1,2,3,4,5,6,7,8,9,10,11]
time_labels = [x if type(x)==str else "{} PM".format(x)
               for x in time_labels]

fig = plt.figure(figsize=(10,5))
plt.xticks(range(24),time_labels,rotation=90)
plt.title("distribution of r/TIL posts with score > 1000")
sns.distplot(T,bins=(24+2*4))
plt.tight_layout()
plt.xlim(0,24)

f_png = "figures/top_TIL_time.png"
plt.savefig(f_png,bbox_inches='tight')
plt.show()
