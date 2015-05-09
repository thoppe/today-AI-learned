# -*- coding: utf-8 -*-

import glob, json, os, time, codecs
import urlparse, string, collections
import urllib2, itertools
from unidecode import unidecode
from src.parsing import tokenize, frequency_table

os.system("mkdir -p db")
os.system("mkdir -p db/model")

PARALLEL_FLAG = True
#PARALLEL_FLAG = False

def reddit_json():
    F_REDDIT = sorted(glob.glob("data/reddit/*.json"))
    for f_json in F_REDDIT:
        with codecs.open(f_json,'r','utf-8') as FIN:
            js = json.load(FIN)
            js["filename"] = f_json
            f_wiki = "data/wikipedia/{}.txt".format(js["name"])
            with open(f_wiki) as FIN:
                js["wiki"]=FIN.read()
            yield js


def split_by_sections(text):
    # Works on mediawiki documents
    text = text.decode('utf-8')

    data = {}
    name = u""
    buffer = []
    for line in text.split(u'\n'):
        
        if line[:2] == "==":
            data[name] = u'\n'.join(buffer)
            name = line.strip().strip("=").strip().lower()
            #name = name.encode('utf-8','replace')
            buffer = []
        else:
            buffer.append(line)

    # Add the last section
    data[name] = u'\n'.join(buffer)

    bad_sections = ["see also","references","external links"]
    for key in bad_sections:
        if key in data:
            data.pop(key)

    return data

def split_by_paragraph(full_text):
    sections = split_by_sections(full_text)

    for section,text in sections.items():
        for paragraph in text.split('\n'):
            paragraph = paragraph.strip()
            if paragraph:
                yield paragraph

def find_TIL_match(js):
    text = js["wiki"]
    url = js["url"]

    wiki_title = url.split('/')[-1].replace('_',' ').lower()
    wiki_title = wiki_title.split('#')[0]
    wiki_title = unidecode(urllib2.unquote(wiki_title))
    wiki_title_tokens = set(wiki_title.split())
   
    TIL_text = js["title"]
    TIL_tokens = set(tokenize(TIL_text))

    # Remove special tokens from TIL
    TIL_tokens = [x for x in TIL_tokens if len(x)>2 and "TOKEN_" not in x]
    
    paragraphs = list(split_by_paragraph(text))
    tokens = map(tokenize,paragraphs)
    freq = frequency_table(tokens)

    # Find words in TIL used in text
    matching_columns = list(set(freq.columns).intersection(TIL_tokens))

    # Idea: Score each paragraph with the highest ranked match
    df = freq[matching_columns]
    
    # Row normalize, thus unique words count for more!
    df /= df.sum(axis=0)
    df.fillna(0,inplace=True)

    # Find the top scoring paragraph
    score = df.sum(axis=1)
    top_idx = score.argmax()
    match_text = paragraphs[top_idx]

    # Now, normalize off the full frequency table for the entropy weight
    freq /= freq.sum(axis=0)
    freq.fillna(0,inplace=True)
    tokens = list(freq.columns[freq.ix[top_idx]>0])
    weights = freq[tokens].ix[top_idx]

    # Convert them into SQL-able formats
    w_str='[{}]'.format(','.join(map("{:0.2f}".format, weights)))

    d_out = {
        "reddit_idx" : js["name"],
        "TIL"        : TIL_text,
        "unprocessed_wikitext"   : match_text,
        "tokens"   : ' '.join(tokens),
        "url"        : url,
        "score"      : js["score"],
        "weights"    : w_str
    }

    key_order = ["reddit_idx", "TIL",
                 "unprocessed_wikitext", "tokens",
                 "url", "score", "weights"]

    data_match = [d_out[key] for key in key_order]

    # Save the remaining parargraphs
    data_unmatch = []
    
    for n in range(len(paragraphs)):
        if n != top_idx:
            tokens = list(freq.columns[freq.ix[n]>0])
            weights = freq[tokens].ix[n]

            assert(len(tokens)==len(weights))
            if len(tokens)>3:
                # Convert them into SQL-able formats
                w_str='[{}]'.format(','.join(map("{:0.2f}".format, weights)))
                t_str = ' '.join(tokens)            
                data_unmatch.append( [t_str, w_str] )

    return data_match, data_unmatch


def data_iterator():

    ITR = itertools.imap(find_TIL_match, reddit_json())
    if PARALLEL_FLAG:
        import multiprocessing
        P = multiprocessing.Pool()
        ITR = P.imap(find_TIL_match, reddit_json())
    
    for k,(data_match,data_unmatch) in enumerate(ITR):
        print k, data_match[1]
        yield data_match, data_unmatch

import sqlite3
conn = sqlite3.connect("db/training.db")

cmd_template = '''
CREATE TABLE IF NOT EXISTS training (
    training_idx  INTEGER PRIMARY KEY AUTOINCREMENT,
    reddit_idx STRING,
    TIL STRING,
    unprocessed_wikitext STRING,
    tokens STRING,
    weights  STRING, -- awful way to do it, but easy enough!
    url  STRING,
    score INTEGER
);

CREATE TABLE IF NOT EXISTS false_positives (
    idx  INTEGER PRIMARY KEY AUTOINCREMENT,
    tokens STRING,
    weights  STRING  -- awful way to do it, but easy enough!
);


'''
conn.executescript(cmd_template)

cmd_insert_match = u'''
INSERT INTO training (reddit_idx, TIL, unprocessed_wikitext, 
                      tokens, url, score, weights)
VALUES (?,?,?,?,?,?,?)
'''

cmd_insert_unmatch = u'''
INSERT INTO false_positives (tokens, weights) VALUES (?,?)
'''

ITR = data_iterator()

for data_match, data_unmatch in ITR:
    conn.execute(cmd_insert_match  , data_match)
    conn.executemany(cmd_insert_unmatch, data_unmatch)
    
conn.commit()
