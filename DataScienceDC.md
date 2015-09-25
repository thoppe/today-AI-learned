# today-AI-learned
[https://github.com/thoppe/today-AI-learned](https://github.com/thoppe/today-AI-learned)
----------

### *[Travis Hoppe](http://thoppe.github.io/)* 
Scientist + DC Hack && Tell

#### [/u/possible_urban_king](https://www.reddit.com/user/possible_urban_king/submitted/)
Artificial Redditor


====
<link rel="stylesheet" href="css/font-awesome-4.3.0/css/font-awesome.min.css">

# The goal

## Train a machine to find 
## new & interesting things

&& Requires a corpus of interesting things...
====*

## Supervised learning
*[r/TIL](http://www.reddit.com/r/todayilearned/)*, a subreddit short for _Today I Learned_
!(figures/TIL_example.png)

====*

## Keep only Wikipedia data
Filter for consistent writing style...
!(figures/TIL_example2.png)

====

## Data collection

Download all popular posts with `score>1000` for 2013 and 2014 (~5000)

Download Wikipedia
Cross-reference each post to the correct Wikipedia _paragraph_
Build True positives (known TIL's)
Build Decoys (other paragraphs in TIL's)
Build unknown samples (rest of Wikipedia*)


### from python import science
`sqlite3`, `requests`, `bs4`, `pandas`, `numpy`, `scikit-learn`, 
`gensim`, `praw`, `wikipedia`, `nltk`, `stemmming.porter2`

&& *Assume that most of Wikipedia isn't interesting...

====*

## Data Wrangling
### Tokenize
    >> "Good muffins cost $3.88\n in New York"
    ['Good', 'muffins', 'cost', 'TOKEN_MONEY', 'in', 'New', 'York', 'TOKEN_EOS']
### Remove "stop words"
    >> "I sat on the rock"
    ['I', 'sat', 'on', 'rock']
### Stem words
    >> stem("factionally")
    'faction'
### "Entropy" vectors
counts the uniqueness of each word to the rest of the entry,
local `TF-IDF` (term frequency-inverse document frequency)

====*

## Feature generation
Used Word2Vec (developed by Google), weighted by local article `TF-IDF`

    >>> model.most_similar(positive=['woman', 'king'], negative=['man'])
    [('queen', 0.50882536), ...]
    >>> model.doesnt_match("breakfast cereal dinner lunch".split())
    'cereal'
    >>> model.similarity('woman', 'man')
    0.73723527
    >>> model['computer']  # raw numpy vector of a word
    array([-0.00449447, -0.00310097,  0.02421786, ...], dtype=float32)

Uses far fewer features to store relationships between words!

&& Also TF-IDF shows reddit is preoccupied with Hitler and Pokemon...[funny story about that](http://www.buzzfeed.com/hamzashaban/godwins-law-is-put-to-the-test)

====*

## Modeling training
Used [Extremely Randomized Trees](http://scikit-learn.org/stable/modules/ensemble.html), variant of Random Tree classifier.
    Training classifier
    Test Accuracy: 0.878;    Test Accuracy on TP: 0.116;   Test Accuracy on TN: 0.998
!(figures/ROC_ExtraTreeClass.png) <<height:550px>> Receiver Operating Curve

====

# Does it work?
_yes! all that sweet sweet front-page karma..._

[TIL The Founder Of Japans Mcdonalds Stated](https://www.reddit.com/r/todayilearned/comments/37bvmu/til_the_founder_of_japans_mcdonalds_stated/) | 4726
[TIL Mike Kurtz An American Burglar Found Out That](https://www.reddit.com/r/todayilearned/comments/3eg5js/til_mike_kurtz_an_american_burglar_found_out_that/) | 4123
[TIL A Woman That Reported 100 Incidents Of](https://www.reddit.com/r/todayilearned/comments/38x454/til_a_woman_that_reported_100_incidents_of/) | 2899
[TIL During The Sentencing Of His War Crimes Trial](https://www.reddit.com/r/todayilearned/comments/3fvl39/til_during_the_sentencing_of_his_war_crimes_trial/) | 1551
[TIL That Art Spiegelman The Creator Of Maus A](https://www.reddit.com/r/todayilearned/comments/36ra0w/til_that_art_spiegelman_the_creator_of_maus_a/) | 1144
[TIL That Once Officially Labeled As Retarded](https://www.reddit.com/r/todayilearned/comments/3cayy3/til_that_once_officially_labelled_as_retarded/) | 640
[TIL Before World War Ii It Was Very Rare For](https://www.reddit.com/r/todayilearned/comments/3cjy9k/til_before_world_war_ii_it_was_very_rare_for/) | 498
[TIL That A Study Showed Those With A Distressed](https://www.reddit.com/r/todayilearned/comments/38iqur/til_that_a_study_showed_those_with_a_distressed/) | 142
[TIL Frankie Fraser A Notorious English Gangster](https://www.reddit.com/r/todayilearned/comments/3e2lw2/til_frankie_fraser_a_notorious_english_gangster/) | 135
[TIL Rafael Quintero A Mexican Drug Trafficker](https://www.reddit.com/r/todayilearned/comments/362d4l/til_rafael_quintero_a_mexican_drug_trafficker/) | 68
...
====
## AI vs Human (Turing test pt. 1)
!(figures/vs_human.png) <<height:700px>>
====
## Big reveal (Turing test pt. 2)
After three months and 60 submissions, I revealed to Reddit
the true nature of `/u/possible_urban_king`.
<br>
====+
<br>
At which the account was promptly banned from posting in r/todayIlearned ...
_thanks anonymous moderator for helping prove the test!_
====
# Thanks, you!

### [Meet The Man Who Gamed Reddit With A Bot](http://www.buzzfeed.com/hamzashaban/today-ai-learned#.glVDa6wR2)
!(figures/BuzzFeed_logo.png) <<transparent>> 


