import praw, os, json, codecs
from pprint import pprint


subreddit_name  = "todayilearned"

# Login 
user_agent = "Subdownloaded 0.1 by /u/hookedon"
agent = praw.Reddit(user_agent=user_agent)
sub = agent.get_subreddit(subreddit_name)


# Create save directories
os.system("mkdir -p data")
os.system("mkdir -p data/reddit")

submissions = sub.search("site:wikipedia",
                         limit=None,
                         sort="top",
                         period="all")


for k,result in enumerate(submissions):
    js = vars(result)

    js["author"] = str(js["author"])
    js["subreddit"] = str(js["subreddit"])

    js.pop("reddit_session")

    name = js["name"]
    jstr = json.dumps(js,indent=2)

    f_out = os.path.join("data","reddit",name+'.json')
    with codecs.open(f_out,"w","utf-8") as FOUT:
        FOUT.write(jstr)

    print k, js["score"], f_out, js["title"][:40]
    
    
