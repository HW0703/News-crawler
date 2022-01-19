# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 15:03:12 2017

@author: user
"""

import time
import requests
from bs4 import BeautifulSoup
import sqlite3

chinatime_news_data = sqlite3.connect('chinatimes.sqlite') #建立資料庫
domain='http://www.chinatimes.com'

def main():
    ChinaTimeCrawler()
    Go_next_page()
    chinatime_news_data.close() #關閉資料庫

    
def ChinaTimeCrawler():
    chinatime_news_data.row_factory=sqlite3.Row
    chinatime_news_data.execute('create table if not exists chinatime(time TEXT,title TEXT,content TEXT,url TEXT UNIQUE);')
    chinatime_news_data.commit()
    
def Go_next_page():     #取得下一頁網頁
    chinatime_news_url=requests.get('http://www.chinatimes.com/realtimenews/')
    page=1
    a=True
    while (True):
        soup = BeautifulSoup(chinatime_news_url.text,'html.parser')
        for next_page in soup.find_all('div',attrs={"class": "listRight"}):
            if(next_page.find('li') == None):
                a = False
        if (a == False):
            break
        page += 1
        domain = 'http://www.chinatimes.com/realtimenews/?page={}'.format(page)
        Go_inside_page(domain)
        time.sleep(1)
        chinatime_news_url=requests.get(domain)
    
def Go_inside_page(get_next_url):       #網頁裡的東西
    res = requests.get(get_next_url)
    soup = BeautifulSoup(res.text,'html.parser')
    for next_page in soup.select('.listRight'):
        for next_page_url in next_page.select('h2'):
            chinatime_news_urls = next_page_url.select('a')[0]['href']
            if (chinatime_news_urls.startswith("http://www.chinatimes.com")==True):
                Add_news_item(chinatime_news_urls)
            else:
                chinatime_news_urls_a = domain + chinatime_news_urls
                Add_news_item(chinatime_news_urls_a)
        time.sleep(1)
    
def Add_news_item(chinatime_news_urls):
    chinatime_news_data.row_factory=sqlite3.Row
    chinatime_news_content=''
    res=requests.get(chinatime_news_urls)
    soup = BeautifulSoup(res.text,'html.parser')
    for news_time in soup.select('time'):     #時間
        chinatime_news_time = news_time.text
    for news_title in soup.select('h1'):           #標題
        chinatime_news_title = news_title.text
    for news_content in soup.select('p'):           #文章
        chinatime_news_content += news_content.text
    chinatime_news_url = res.url                        #網址
    Get_news_item(chinatime_news_time, chinatime_news_title, chinatime_news_content,chinatime_news_url)
    chinatime_news_data.commit()
    
    
def Get_news_item(time,title,content,url):  
    chinatime_news_data.row_factory=sqlite3.Row
    chinatime_news_data.execute('insert or ignore into chinatime(time,title,content,url) values(?,?,?,?) ',(time,title,content,url)) #資料庫裡的文件
    chinatime_news_data.commit()


if __name__ == '__main__':main()