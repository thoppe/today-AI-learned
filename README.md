# today-AI-learned

#### Hello Reddit! I'm the semi-autonomous bot [`u/possible_urban_king`](https://www.reddit.com/user/possible_urban_king/submitted/)

TLDR; I was created to machine learn reddit's [r/today-I-learned](https://www.reddit.com/r/todayilearned/) (TIL) subreddit for new and interesting things. If karma/upvotes measure success, I passed the [Turing test](https://en.wikipedia.org/wiki/Turing_test).

----

# Description
_from the author (Travis Hoppe)[http://thoppe.github.io/]_

It is an exciting time right now if you're even the least bit interested in Machine Learning.
With modest effort, anyone with an idea can transform it into a working algorithm (though results vary greatly).
I've been a fan of the subreddit [r/today-I-learned](https://www.reddit.com/r/todayilearned/) for some time and I thought it would be an interesting challenge to train an algorithm over.
In contrast to traditional machine learning tasks such as image recognition or time-series prediction, the concept of an _interesting_ reddit post is vague and undefined, which makes it an exciting topic to study!
  
The metric for a successful post is the upvote tally.
These votes are aggregated poll over the Reddit vox populi and in a limited sense constitute tests for intelligence.
In TIL especially, this requires synthesis of knowledge to find things interesting to a human.
If a machine were to act like a (human) Redditor, it would have emulate this task in new and novel ways.

In this context [`u/possible_urban_king`](https://www.reddit.com/user/possible_urban_king/submitted/) passes the Turing test.
Over the last three months I've been running an experiment and posted about 50 submissions to TIL.
The bot's posts have made it to the front page multiple times and the majority of posts are well-received (see results).

The bot was trained over a selection of previously successful TIL posts (see methods) that used Wikipeida as a source.
Classification worked well, sometimes too well.
I found that media characters (books, movies, etc...) were disproportionately tagged as interesting (and they would be too, if they were real people!).
Additionally, sections in Wikipedia that were salacious or required a [Citation Needed] were often removed by the time they were to be posted.

+ Semi-autonomous?

It turns out writing the title of a post is really hard, even for the human expeirmenter. [`u/possible_urban_king`](https://www.reddit.com/user/possible_urban_king/submitted/) is semi-autonomous in this sense since a human still wrote the post and submitted by hand. I was however, limited to use the information taken from the paragraph marked that was marked as interesting.

+ What algorithm/classifier?

[Extremely Random Trees](http://scikit-learn.org/stable/modules/ensemble.html#extremely-randomized-trees).

+ Why the name `possible_urban_king`?

It's a [colorless green idea](https://github.com/thoppe/Colorless-Green-Ideas).

-----
  
# Results

-----

# Methods

## Data collection
  
Supervised machine learning requires a massive tagged collection of high-quality data to be effective. Fortunately the past submissions of to r/TIL have done just that. Redditors have carefully curated a selection of posts that they collectively find interesting through their voting system. We can filter these posts to just those that point to Wikipedia as a source. This way, the source of each post uses a somewhat standardized language and grammar.

##### [src/subreddit_dl.py](src/subreddit_dl.py)

Initally I started with the top 1000 posts of all-time (due to an API restriction in reddit's search) using [praw](https://praw.readthedocs.org/en/). Ultimately however, I extended that to all posts that had a score of > 1000 in the years 2013 and 2014 (resulting in about 5000 quality TIL posts) using an alternate database.

##### [src/wikipedia_dl.py](src/wikipedia_dl.py)

From here it is relatively easy to download a parsed down versed of the wiki page linked to by the reddit post.

## Data wrangling

##### [src/attribute_TIL.py](src/attribute_TIL.py)

Somehow, we have to link the pithy one-line TIL title to the correct paragraph in the Wikipedia article. This is a non trivial task, as simple word frequencies are not enough. Ultimately I settled on a sort of "word-entropy". That is, each paragraph was stripped to it's unique words and these sets all formed a frequency vector for each paragraph. These vectors were normalized so that the unique words in each paragraph carried more weight. Then we took the title of the TIL post and compared it to the vectors of each paragraph settling on the paragraph with the closest match. This turns out to work surprisingly well.

Additionally, I saved the non-matching paragraphs as some useful false positives.

##### [src/build_decoy_db.py](src/build_decoy_db.py)

The next step was to prep the Wikipedia corpus.
Using a full XML corpus of Wikipedia (not provided and parsed with [`bs4`](http://www.crummy.com/software/BeautifulSoup/bs4/doc/)), I tokenized and stemmed each paragraph of text for each article. This uses both [`nltk`](http://www.nltk.org/) for the word tokenization & stop words and the porter2 stemmer from the aptly named package [`stemming`](https://pypi.python.org/pypi/stemming/1.0).

This creates a rather massive SQLite database with each paragraph and the associated meta-data (like title, paragraph number, word-entropy, ...). Since there are many millions of assorted paragraphs (and I assume very few of them are interesting), I am going to use a random sampling of some of these as True Negatives in my machine learning. 

## Machine Learning

##### [src/build_features.py](src/build_features.py)

Initially, I experimented with a simple word frequency as my feature vector. While this works for toy problems, the corpus of Wikipedia needed a smarter way to condense down the data. Fortuntetly, a neat textual feature generator, Word2Vec (developed by Google) is available in [`gensim`](https://radimrehurek.com/gensim/).

Using Word2Vec requires two complete passes over the data, though it allows you to use an iterator making the memory requirements rather small.

##### [src/train.py](src/train.py)

Here, perhaps lies the most contentious part of the project, the construction of the classifier. In the end, I settled for the Extremely Random Trees implementation in [`scikit-learn`](http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html). This classifier, while fairly poor at detecting new true positives at about 10%, was extremely proficient at marking the true negatives. Since the assumption is that most of Wikipedia is, in fact, quite boring, this will help narrow down the results immensely.

    Training classifer
    Test Accuracy: 0.878
    Test Accuracy on TP: 0.116
    Test Accuracy on TN: 0.998

![](figures/ROC_ExtraTreeClass.png)
  

##### [src/score.py](src/score.py)

With the classifier solved, the next step is score each and every paragraph in Wikipedia. The classifier marks about 6 per 10000 as potential candidates.

##### [src/report.py](src/report.py)

With the positives marked, we need to prepare the potentially interesting things to a human-readable format!
Report starts building a new database that contains only the positive entries and the associated wikipedia text from the original source.

##### [src/cross_reference.py](src/cross_reference.py)

Nobody likes a repost (unless it's better, or more aptly timed...), so we need to find out what has already been posted to reddit.
To do so, we need a proper search name of the wikipedia article.
The module `mediawiki-utils` can do this, but stupidly requires python3.
Thus the cross-reference program makes a system call to properly encode name as a search query for reddit.
We then take the top search result (if exists) and store it; this info will serve as the criteria for a post/repost.

##### [src/plot_times.py](src/plot_times.py)

With the potential TIL candidates identified, let's find the best time to post!
Note that we are going to posit that post time has a casual relationship with the ultimate score.
Since reddit is dynamic and viewership is dependent on a steady-stream of upvotes, this should be a reasonable assumption.
Going back over our training set, we can map the distribution of times for a r/TIL post:

![](figures/top_TIL_time.png)

it seems like the sweet spot for a submission is between 9AM-11AM!

What about the bottom r/TIL posts, those that had a score of < 1000? Considering only the ones we found with our algorithm, the posting time is dramatically different:

![](figures/bottom_TIL_time.png)

##### [src/mine_submissions.py](src/mine_submissions.py)

Since we are going to have quite a few false positives, we setup a simple script to help determine quality TIL's.
A random unlabeled TIL is pull from the database that hasn't been posted already and is opened on both the screen and the browser to quicky determine if it is "something worth learning".
This script show both the tagged interesting paragraph and the cooresponding wikipedia page.
There is a simple prompt that allows you to mark an item to post later.

--------

##### Presentations/Media

From the [DC Hack and Tell](http://www.meetup.com/DC-Hack-and-Tell/) Round 20: Severe Municipal Jazz, May 11, 2015, [presentation link](http://thoppe.github.io/today-AI-learned/index.html).