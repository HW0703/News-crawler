# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 23:28:55 2017

@author: user
"""

import time
import requests
from bs4 import BeautifulSoup
import sqlite3

udn_news_data = sqlite3.connect('United_Daily_News.sqlite') #建立資料庫
domain='https://udn.com'

def main():
    UDNCrawler()
    Go_next_page()
    udn_news_data.close() #關閉資料庫

    
def UDNCrawler():
    udn_news_data.row_factory=sqlite3.Row
    udn_news_data.execute('create table if not exists udn(time TEXT,title TEXT,content TEXT, url TEXT UNIQUE);')
    udn_news_data.commit()
    
def Go_next_page():     #取得下一頁網頁
    page=0
    while (True):
        if (page == 81):
            break
        page += 1
        get_next_url = 'https://udn.com/news/breaknews/1/0/{}#breaknews'.format(page)
        Go_inside_page(get_next_url)
        time.sleep(1)
    
def Go_inside_page(get_next_url):       #網頁裡的東西
    res = requests.get(get_next_url)
    res.encoding='utf-8'
    soup = BeautifulSoup(res.text,'html.parser')
    for news in soup.select('.area_body'):
        for udn_news_urls in news.select ('h2'):
            udn_news_url = udn_news_urls.select('a')[0]['href']
            if (udn_news_url.startswith("https://udn.com")==True):
                Add_news_item(udn_news_url)
            else:
                udn_news_url = domain + udn_news_urls.select('a')[0]['href']
                Add_news_item(udn_news_url)
        time.sleep(1)
    
def Add_news_item(udn_news_url):
    udn_news_data.row_factory=sqlite3.Row
    udn_news_content=''
    res=requests.get(udn_news_url)
    res.encoding='utf-8'
    soup = BeautifulSoup(res.text,'html.parser')
    for news_time in soup.select('.story_bady_info_author'):     #時間
        udn_news_time = news_time.text
    for news_title in soup.select('#story_art_title'):           #標題
        udn_news_title = news_title.text
    for news in soup.select('#story_body_content'):
        for news_content in news.select('p'):          #文章
            udn_news_content += news_content.text
    udn_news_url = res.url                        #網址
    Get_news_item(udn_news_time, udn_news_title, udn_news_content,udn_news_url)
    udn_news_data.commit()
    
    
def Get_news_item(time,title,content,url):  
    udn_news_data.row_factory=sqlite3.Row
    udn_news_data.execute('insert into udn(time,title,content,url) values(?,?,?,?) ',(time,title,content,url)) #資料庫裡的文件
    udn_news_data.commit()


if __name__ == '__main__':main()