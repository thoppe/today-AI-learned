import sqlite3
import itertools
import numpy as np
from parsing import tokenize, frequency_table, paragraph_iter

def token_block_iter(title,html):

    wiki  = paragraph_iter(html)

    token_table = map(tokenize, wiki)
    freq = frequency_table(token_table)

    wiki_title = unicode(wiki.title)
    wiki_title_tokens = set(tokenize(wiki_title))

    wiki_index = wiki.id

    # Column normalize frequency table
    freq /= freq.sum(axis=0)

    for para_n,tokens in enumerate(token_table):
        tokens = set(tokens).difference(wiki_title_tokens)
        tokens = list(tokens)
        
        local_freq = freq[tokens].ix[para_n]
        yield para_n, tokens, wiki_index, wiki_title, local_freq

    
def SQL_result(item):
    idx,title,html,length= item
    print "Processing:", title,idx

    all_data = []
    for result in token_block_iter(title, html):
        para_n, tokens, wiki_index, wiki_title, frq = result
        f_str='[{}]'.format(','.join(map("{:0.2f}".format,
                                         list(frq.values))))
        
        tokens = ' '.join(tokens)
        data = [wiki_index,title,para_n,tokens,f_str]
        all_data.append(data)
    return all_data

if __name__ == "__main__":
    f_wiki = "/media/travis/Seagate Expansion Drive/data_dump/wiki.db"
    conn = sqlite3.connect(f_wiki, check_same_thread=False)

    conn_decoy = sqlite3.connect("db/decoy.db")

    cmd_template = '''
    CREATE TABLE IF NOT EXISTS decoy (
        decoy_idx  INTEGER PRIMARY KEY AUTOINCREMENT,
        wikipedia_idx INTEGER,
        wikipedia_title STRING,
        weights STRING,    -- awful way to do it, but easy enough!
        paragraph_count INTEGER,
        tokens STRING
    )
    '''
    conn_decoy.executescript(cmd_template)

    cmd_search = "SELECT * FROM wiki ORDER BY title LIMIT 7000"
    cmd_search = "SELECT * FROM wiki ORDER BY title"
    WIKI = conn.execute(cmd_search)
    ITR  = itertools.imap(SQL_result, WIKI)

    import multiprocessing
    P = multiprocessing.Pool()
    ITR  = P.imap(SQL_result, WIKI)

    cmd_insert = u'''
    INSERT INTO decoy (
    wikipedia_idx,wikipedia_title,
    paragraph_count,tokens,weights) 
    VALUES (?,?,?,?,?)
    '''

    for result in ITR:
        conn_decoy.executemany(cmd_insert, result)
    conn_decoy.commit()

