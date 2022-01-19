# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 19:33:47 2017

@author: user
"""
import time
import requests
from bs4 import BeautifulSoup
import sqlite3

apple_news_data = sqlite3.connect('apple.sqlite') #建立資料庫
domain='http://www.appledaily.com.tw'

def main():
    AppleCrawler()
    Go_next_page()
    apple_news_data.close() #關閉資料庫
    
def AppleCrawler():
    apple_news_data.row_factory=sqlite3.Row
    apple_news_data.execute('create table if not exists apple(time TEXT,title TEXT,content TEXT, url TEXT UNIQUE);')
    apple_news_data.commit()
    
def Go_next_page():     #取得下一頁網頁
    get_next_url=''
    apple_news_url=requests.get('http://www.appledaily.com.tw/realtimenews/section/new/')
    while (True):
        end_page_url = get_next_url
        soup = BeautifulSoup(apple_news_url.text,'html.parser')
        for next_page in soup.select('.page_switch.lisw.fillup'):
            for next_page_url in next_page.select('a'):
                page_url = next_page_url['href']
                Go_inside_page(domain + page_url)
        get_next_url = page_url
        if(end_page_url == get_next_url):       #判斷是否為最後一頁
            break
        time.sleep(1)
        apple_news_url=requests.get(domain + get_next_url)
    
def Go_inside_page(get_next_url):       #網頁裡的東西
    res = requests.get(get_next_url)
    soup = BeautifulSoup(res.text,'html.parser')
    for news in soup.select('.rtddt'):
        apple_news_urls = news.select('a')[0]['href']
        if (apple_news_urls.startswith("http://www.appledaily.com.tw")==True):
            Add_news_item(apple_news_urls)
        else:
            apple_news_urls = domain + news.select('a')[0]['href']
            Add_news_item(apple_news_urls)
        time.sleep(1)
    
def Add_news_item(apple_news_urls):
    apple_news_data.row_factory=sqlite3.Row
    apple_news_content=''
    res=requests.get(apple_news_urls)
    soup = BeautifulSoup(res.text,'html.parser')
    for news_time in soup.select('.gggs time'):     #時間
        apple_news_time = news_time.text
    for news_title in soup.select('#h1'):           #標題
        apple_news_title = news_title.text
    for news_content in soup.select('p'):           #文章
        apple_news_content += news_content.text
    apple_news_url = res.url                        #網址
    Get_news_item(apple_news_time, apple_news_title, apple_news_content,apple_news_url)
    apple_news_data.commit()
    
    
def Get_news_item(time,title,content,url):  
    apple_news_data.row_factory=sqlite3.Row
    apple_news_data.execute('insert into apple(time,title,content,url) values(?,?,?,?) ',(time,title,content,url)) #資料庫裡的文件
    apple_news_data.commit()


if __name__ == '__main__':main()

    
   
    