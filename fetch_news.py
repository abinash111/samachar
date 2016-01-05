#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import sumy, tweepy, time, requests, json, praw
import private_data
from goose import Goose

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

import requests
from BeautifulSoup import BeautifulSoup

LANGUAGE = "english"
SENTENCES_COUNT = private_data.sen_count

banned_words=private_data.banned_words
blacklist=private_data.blacklist

def is_blotted(sentence, ban_words):
    for word in ban_words:
        if word in sentence.lower():
            return True
    return False
    
def print_news(url, content='title'):
    #parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
    g=Goose()
    
    article=g.extract(url=url)
    
    #If there is a meta description available, print that else go for
    #summarize
    if content=='full' and article.meta_description:
        print(article.meta_description)
        return
    
    news_text=article.cleaned_text
    
    parser = PlaintextParser.from_string(news_text, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    
    if content=='title' or content=='full':
        #Print article title
        print('\t* '+str(article.title.encode('ascii', 'ignore')))
    
    if content=='full':
        #Print a n-line summary
        for sentence in summarizer(parser.document, SENTENCES_COUNT):
            print(sentence)
    return

def reddit_news(NEWS_LIMIT):
    r=praw.Reddit(user_agent=private_data.reddit_ua)
    submissions=r.get_subreddit('IndiaNews').get_new(limit=NEWS_LIMIT)
    for topic in submissions:
        if topic.domain not in blacklist:
            if not(is_blotted(topic.title, banned_words)):
                print_news(topic.url, 'title')
    return 0
    
def new_IE_odia(NEWS_LIMIT):
    
    urlIEO='http://www.newindianexpress.com/states/odisha/'
    
    news_links=[]
    
    page=requests.get(urlIEO)
    soup=BeautifulSoup(page.text)
    content=soup.find('div', attrs={'class':'content'})
    links=content.findAll('a')
    #Make a list of the URLs
    for link in links:
        news_links.append(link['href'])
    
    #Print the news articles using summarize
    for link in news_links[:NEWS_LIMIT]:
        print_news(link, 'title')
    return

def otv_news(NEWS_LIMIT):
    #http://www.odishatv.in/category/odisha/
    urlOTV='http://www.odishatv.in/'
    page=requests.get(urlOTV)
    page=page.text[page.text.find('ODISHA'):-1]
    soup=BeautifulSoup(page)

    links=[]
    contents=soup.findAll('div', attrs={'class':'td_block_inner'}) #td_uid_5_5686401802298

    for content in contents:
        sub_section=content.findAll('h3', attrs={'class':'entry-title td-module-title'})
        for section in sub_section:
            links.append(section.find('a'))
    
    news_headlines=[]
    
    for link in links[:NEWS_LIMIT]:
        print('\t* '+str(link['title'].encode('ascii', 'ignore')))
        news_headlines.append(link['title'].encode('ascii', 'ignore'))
    return

def otv_trending(NEWS_LIMIT):
    #http://www.odishatv.in/category/odisha/
    urlOTV='http://www.odishatv.in/'
    page=requests.get(urlOTV)
    soup=BeautifulSoup(page.text)
    
    content=soup.find('div', attrs={'class':'td-trending-now-wrapper'})
    links=content.findAll('a')
    
    news_headlines=[]
    
    for link in links[:NEWS_LIMIT]:
        if str(link.text.encode('ascii', 'ignore')):
            print('\t* '+str(link.text.encode('ascii', 'ignore')))
            news_headlines.append(link.text.encode('ascii', 'ignore'))
    return

def the_samaya(NEWS_LIMIT):
    
    urlSamaya='http://odishasamaya.com/news/category/odisha'
    
    page=requests.get(urlSamaya)
    soup=BeautifulSoup(page.text)
    
    content=soup.find('div', attrs={'id':'colorcontentblock'})
    links=content.findAll('a', attrs={'rel':'bookmark'})
    
    news_links=[]
    news_headlines=[]
    
    for link in links[:NEWS_LIMIT]:
        print('\t* '+str(link.text.encode('ascii','ignore')))
        news_links.append(link['href'])
        news_headlines.append(str(link.text.encode('ascii','ignore')))
    return

def toi(NEWS_LIMIT):
    
    url_ToI='http://timesofindia.indiatimes.com/'
    
    page_ToI=requests.get(url_ToI)
    soup_ToI=BeautifulSoup(page_ToI.text)
    section=soup_ToI.findAll('ul', attrs={'data-vr-zone':'latest', 'class':'list9'})[0]
    return [str(link.text.encode('ascii','ignore')) for link in section.findAll('a')[:NEWS_LIMIT] if (str(link.text.encode('ascii','ignore'))) and not('Adv:'in str(link.text.encode('ascii','ignore')))]
    
def the_hindu(NEWS_LIMIT):
    
    url_TheHindu='http://www.thehindu.com/news/?service=rss'
    
    page_TheHindu=requests.get(url_TheHindu)
    soup_TheHindu=BeautifulSoup(page_TheHindu.text)
    
    return [str(item.findAll('title')[0].text.encode('ascii','ignore')) for item in soup_TheHindu.findAll('item')[:NEWS_LIMIT]]    

if __name__ == '__main__':
    #print('___NEWS FROM REDDIT.COM___')
    #reddit_news(10)
    #print('___THE NEW INDIAN EXPRESS ODISHA___')
    #new_IE_odia(10)
    #print('___OTV NEWS___')
    #otv_news(10)
    #print('___OTV Trending___')
    #otv_trending(10)
    #print('___THE SAMAYA___')
    #the_samaya(10)
    #print('___THE TIMES OF INDIA___')
    #print(toi(20))
    #print('___THE HINDU___')
    #print(the_hindu(20))
