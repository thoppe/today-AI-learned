import glob, json, os, time, codecs
import urlparse
import requests
import wikipedia, urllib2

os.system("mkdir -p data")
os.system("mkdir -p data/wikipedia")

import logging
logging.basicConfig(filename='broken_json.log',level=logging.DEBUG)

def reddit_json():
    F_REDDIT = sorted(glob.glob("data/reddit/*.json"))
    for f_json in F_REDDIT:
        with open(f_json) as FIN:
            js = json.load(FIN)
            js["filename"] = f_json
            yield js

def save_page(name,f_html):
        
    r = wikipedia.page(name)
    text = r.content

    with codecs.open(f_html,'w','utf-8') as FOUT:
        print "Downloaded ", f_html
        print
        FOUT.write(text)
        time.sleep(.2)


for js in reddit_json():
    url, title = js["url"], js["title"]
    r_id = js["name"]

    url = urllib2.unquote(url.encode('utf-8'))    
    name = url.split('/')[-1]

    search_bit = "index.php?title="
    if search_bit in name:
        url  = url.replace(search_bit,'')
        name = url.split('/')[-1]


    print js["filename"]
    f_html = "data/wikipedia/{}.txt".format(r_id)
    
    if not os.path.exists(f_html):
        name = name.split('#')[0].split('?')[0].split("&")[0]
        name = name.replace('_',' ')
        name = name.lower()

        #print url
        #print name
        #print "Searching for", name

        try:
            save_page(name,f_html)
        except Exception as Ex:
            logging.warning(f_html)
            print Ex
            
