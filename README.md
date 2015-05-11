# today-AI-learned
Machine learning reddit's [today-I-learned](https://www.reddit.com/r/todayilearned/) (TIL) subreddit to mine for new and interesting things.

# Data collection
  
Supervised machine learning requires a massive tagged collection of high-quality data to be effective. Fortunately the past submissions of to r/TIL have done just that. Redditors have carefully curated a selection of posts that they collectively find interesting through their voting system. We can filter these posts to just those that point to Wikipedia as a source. This way, the source of each post uses a somewhat standardized language and grammar.

#### [src/subreddit_dl.py](src/subreddit_dl.py)

Initally I started with the top 1000 posts of all-time (due to an API restriction in reddit's search) using [praw](https://praw.readthedocs.org/en/). Ultimately however, I extended that to all posts that had a score of > 1000 in the years 2013 and 2014 (resulting in about 5000 quality TIL posts) using an alternate database.

#### [src/wikipedia_dl.py](src/wikipedia_dl.py)

From here it is relatively easy to download a parsed down versed of the wiki page linked to by the reddit post.



1. Download 1000 top TIL stories on that have wikipedia sources
2. Download cooresponding Wikipages
4. Section-ify the wikipages
5. Determine which section article refers to
6. Prep raw text database of full wikipedia

7. Start feature training!

python attribute_TIL.py 
python build_decoy_db.py
python train.py
python score.py

  
python attribute_TIL.py && python build_decoy_db.py && python train.py && python score.py