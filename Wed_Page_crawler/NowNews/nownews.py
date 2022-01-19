# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 18:12:58 2017

@author: user
"""

import time
import requests
from bs4 import BeautifulSoup
import sqlite3
import re

nownews_news_data = sqlite3.connect('nownews.sqlite') #建立資料庫
domain='https://www.nownews.com'

def main():
    NownewsCrawler()
    Go_next_page()
    nownews_news_data.close() #關閉資料庫

    
def NownewsCrawler():
    nownews_news_data.row_factory=sqlite3.Row
    nownews_news_data.execute('create table if not exists nownews(time TEXT,title TEXT,content TEXT, url TEXT UNIQUE);')
    nownews_news_data.commit()
    
def Go_next_page():     #取得下一頁網頁
    for page in range (1,50+1):
        get_next_url = 'https://www.nownews.com/instant?page={}'.format(page)
        Go_inside_page(get_next_url)
        time.sleep(1)
    
def Go_inside_page(get_next_url):       #網頁裡的東西
    res = requests.get(get_next_url)
    soup = BeautifulSoup(res.text,'html.parser')
    for next_page in soup.find_all('div', attrs={'data-reactid': '78'}):
        for next_page_url in next_page.select('a'):
            nownews_news_url = next_page_url['href']
            nownews_news_urls = domain + nownews_news_url
            Add_news_item(nownews_news_urls)
            time.sleep(1)
    
def Add_news_item(nownews_news_urls):
    nownews_news_data.row_factory=sqlite3.Row
    nownews_news_content=''
    res=requests.get(nownews_news_urls)
    soup = BeautifulSoup(res.text,'html.parser')
    for news_time in soup.find_all('div',attrs={"class": "authorArea_1gv4of8"}):     #時間
        nownews_news_time = re.sub('[^0-9/ :]', "",news_time.text)
    for news_title in soup.select('.title_143mah6'):           #標題
        nownews_news_title = news_title.text
    for news_content in soup.select('p'):           #文章
        nownews_news_content += news_content.text        
    Get_news_item(nownews_news_time, nownews_news_title, nownews_news_content,nownews_news_urls)
    nownews_news_data.commit()
    time.sleep(1)
    
    
def Get_news_item(time,title,content,url):  
    nownews_news_data.row_factory=sqlite3.Row
    nownews_news_data.execute('insert or ignore into nownews(time,title,content,url) values(?,?,?,?) ',(time,title,content,url)) #資料庫裡的文件
    nownews_news_data.commit()


if __name__ == '__main__':main()