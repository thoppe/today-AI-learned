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

## Keep only wikipedia data
Filter for consistant writing style...
!(figures/TIL_example2.png)

====

## Data collection

+ Download all popular posts with `score>1000` for 2013 and 2014 (~5000)
+ Download wikipedia
+ Cross-reference each post to the correct wikipedia _paragraph_

+ Built True positives (known TIL's)
+ Built Decoys (other paragraphs in TIL's)
+ Built unknown samples (rest of Wikipedia)

&& Assume that most of wikipeida isn't interesting...

====*

## Data Wrangling
### Tokenize
    >> "Good muffins cost $3.88\nin New York"
    ['Good', 'muffins', 'cost', 'TOKEN_MONEY', 'in', 'New', 'York', 'TOKEN_EOS']
### Remove "stop words"
    >> "I sat on the rock"
    ['I', 'sat', 'on', 'rock']
### Stem words
    >> stem("factionally")
    'faction'
### "Entropy" vectors
counts the unqiueness of each word to the rest of the entry,
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

====*

## Modeling training
Used [Extremely Random Trees](http://scikit-learn.org/stable/modules/ensemble.html), variant of Random Tree classifier.
    Training classifer
    Test Accuracy: 0.878;    Test Accuracy on TP: 0.116;   Test Accuracy on TN: 0.998
!(figures/ROC_ExtraTreeClass.png) <<height:550px>>

====
# Does it work?




# Thanks you!

<div style="footnote">
Looking for an overpowered scientist turned analyst/developer? Let's talk!<br>*travis.hoppe @ gmail.com*
</div>


