# today-AI-learned
_(five minute hack-and-tell version)_

*[Travis Hoppe](http://thoppe.github.io/)*
----------
[https://github.com/thoppe/today-AI-learned](https://github.com/thoppe/today-AI-learned)
<link rel="stylesheet" href="css/font-awesome-4.3.0/css/font-awesome.min.css">

====
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

+ Download all popular posts with `score>1000` for 2013 and 2014 (~5000)
+ Download Wikipedia
+ Cross-reference each post to the correct Wikipedia _paragraph_
+ Built True positives (known TIL's)
+ Built Decoys (other paragraphs in TIL's)
+ Built unknown samples (rest of Wikipedia*)


### Use all the tools!
Project uses modules `sqlite3`, `requests`, `bs4`, `pandas`, `numpy`, `scikit-learn`, `gensim`, `praw`, `wikipedia`, `nltk`, `stemmming.porter2`

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

&& Also TF-IDF shows reddit is preoccupied with Hitler and Pokemon...

====*

## Modeling training
Used [Extremely Random Trees](http://scikit-learn.org/stable/modules/ensemble.html), variant of Random Tree classifier.
    Training classifier
    Test Accuracy: 0.878;    Test Accuracy on TP: 0.116;   Test Accuracy on TN: 0.998
!(figures/ROC_ExtraTreeClass.png) <<height:550px>>

====

# Does it work?
Yes! (Examples incoming). Still requires a human to construct titles and filter. Mistaken concentrates on movie & book plot summaries (if they happened in real life they would be exciting!).

====+

# Does it pass the Turning test?
shhhhh.... secretly submitting to reddit soon

====*
# Examples!

## Bubble wrap

"Bubble wrap" is a generic trademark owned by Sealed Air Corporation. In 1957 two inventors named Alfred Fielding and Marc Chavannes were *attempting to create a three-dimensional plastic wallpaper*. Although the idea was a failure, they found that what they did make could be used as packing material. Sealed Air Corp. was co-founded by Alfred Fielding.
====*
# Examples!

##DineEquity

Julia Stewart, who originally *worked as a waitress at IHOP and worked her way up through the restaurant industry, became Chief Executive Officer* of IHOP Corporation. She had previously been President of Applebee’s, but left after being overlooked for that company's CEO position. She became CEO of IHOP in 2001, and returned to manage her old company due to the acquisition.

====*
# Examples!

###George R. R. Martin

Martin is *opposed to fan fiction*, believing it to be copyright infringement and a *bad exercise for aspiring writers*.


====


# Thanks you!

<div style="footnote">
Looking for an overpowered scientist turned analyst/developer? Let's talk!<br>*travis.hoppe @ gmail.com*
</div>


