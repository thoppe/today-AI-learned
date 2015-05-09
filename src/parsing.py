import string, itertools, re
from unidecode import unidecode
import pandas as pd

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from stemming.porter2 import stem as port_stem

import bs4

stopwords = stopwords.words('english') + ["til"]
simple_tokens = ["'",'"','.','?','!',"''",':','``',',',')','(']

simple_tokens = map(unicode, simple_tokens)
stopwords = map(unicode, stopwords)

alpha_only = re.compile("^[a-zA-Z]+$")

def special_token_matching(token):

    if not token:
        return "TOKEN_EMPTY"

    if token[0] == "$":
        return "TOKEN_PRICE"

    try:
        float(token)
        return "TOKEN_NUMBER"
    except:
        # If there are no alpha characters, mark as TOKEN_SYMBOL
        if not alpha_only.search(token):
            return "TOKEN_SYMBOL"

    return token
            
def tokenize(text, stem=True):

    '''
    # REMOVE TIL and simple_tokens and stop words
    Map numbers -> TOKEN_NUMBER
    Map price   -> TOKEN_PRICE
    '''

    text = unicode(unidecode(text))
    tokens = map(string.lower, word_tokenize(text))

    if stem:
        tokens = map(port_stem, tokens)

    title_tokens = [special_token_matching(x)
                    for x in tokens if
                    x not in simple_tokens and
                    x not in stopwords]   

    return title_tokens

def frequency_table(tokens):
    '''
    Determines the relative frequencies of each word to the article (corpus).
    Unique words may signify ideas that are new to the corpus (hypothesis).
    '''

    # Map down freq. per paragraphs to unity
    n_para = len(tokens)
    tokens = map(set, tokens)


    # Find list of unique words
    unique = set().union(*tokens)
    
    
    df = pd.DataFrame(0, columns=unique,
                      index=range(n_para),
                      dtype=float)

    #print df.columns
    for k, vals in enumerate(tokens):
        df.ix[k][list(vals)] += 1

    return df

##############################################################

class paragraph_iter(object):
    def __init__(self, html):
        self.soup  = bs4.BeautifulSoup(html)

        doc = self.soup.doc
        
        self.id    = doc["id"]
        self.title = doc["title"]
        self.url   = doc["url"]

        self.paragraphs = []
        blocks = doc.findAll(text=True,recursive=False)
        for block in blocks:
            for p in block.split('\n'):
                p = p.strip()
                if len(p)>20:
                    self.paragraphs.append(p)

    def __getitem__(self,i):
        return self.paragraphs[i]
