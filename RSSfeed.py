from nltk.corpus.reader.plaintext import PlaintextCorpusReader
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import date, datetime
from dateutil import parser
from bs4 import BeautifulSoup
import feedparser
import nltk
import lxml
import requests
import numpy
import time
import sqlite3
#import Generic_parser
#import WebTest
#import pyOpenSsl

class formattedArticle(object):

    def __init__(self, h1, a1, d1, l1):
        self.headline = h1
        self.article = a1
        self.date = d1
        self.link = l1
        self.sentiment = 0
        self.sia = SentimentIntensityAnalyzer()
        # self.sia.lexicon.update("/home/Phil/Downloads/LoughranMcDonald_MasterDictionary_2016.csv")

    def save_to_sql(self):
        # format the date
        self.date = self.date.replace('+0000', '')
        self.date = parser.parse(self.date)

        # sentiment scoring
        self.sentiment = self.sia.polarity_scores(self.article)['compound']

        # Remove all the new line and carridge returns from the article for formatting
        self.article = self.article.replace('\r', '')
        self.article = self.article.replace('\n', '')
        self.article = self.article.replace('\r\n', '')

        # This line removes embedded share buttons for facebook, twitter ect
        self.article = self.article.replace('.bwalignc {text-align: center !important;} .bwalignl {text-align: left'
                                             ' !important;} .bwcellpmargin {margin-bottom: 0px !important; margin-top'
                                             ': 0px !important;} .bwpadl0 {padding-left: 0.0px !important;} '
                                             '.bwtablemarginb {margin-bottom: 10.0px !important;} .bwvertalignt'
                                             ' {vertical-align: top !important;} ;} ', '')
        # connect to the database
        connection = sqlite3.connect("/home/Phil/store/News2")
        cursor = connection.cursor()
        # try to add the feed into the database
        try:
            cursor.execute("INSERT INTO data VALUES (?,?,?,?,?)", [self.date, self.headline, self.article,  self.link, self.sentiment])
            print("Added article to DB")
        except sqlite3.IntegrityError:
            print("error, already in db")
        # close the connection
        connection.commit()
        connection.close()


# Parses the article and saves it to the sql file
def getarticle(entry):
    headline = entry['title']
    url = entry['link']
    date = entry['published']
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'lxml')
    links = [e.get_text() for e in soup.find_all('p')]
    article = '\n'.join(links)
    print(headline)
    articleforsaving = formattedArticle(headline, article, date, url)
    articleforsaving.save_to_sql()

d = feedparser.parse('http://finance.yahoo.com/rss/headline?s=dji,mmm,axp,aapl,ba,cat,cvx,csco,ko,dis,dwdp,xom,gs,hd'
                     ',ibm,intc,jnj,jpm,mcd,mrk,msft,nke,pfe,pg,trv,utx,unh,vzv,wmt,wba')

print(d['feed']['description'])

if len(d) >= 2:
    for i in range(len(d)):
        getarticle(d.entries[i])
else:
    getarticle(d.entries[0])
