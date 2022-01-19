# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 01:49:48 2017

@author: user
"""

import time
import requests
from bs4 import BeautifulSoup
import sqlite3
from selenium import webdriver
import re

ETnews_news_data = sqlite3.connect('ETnews.sqlite') #建立資料庫
domain='http://www.ettoday.net'
drive_path="D:/Practical-Python-Program/chromedriver/chromedriver.exe"

def main():
    ETnewsCrawler()
    Go_inside_page()
    
    ETnews_news_data.close() #關閉資料庫
    
def ETnewsCrawler():
    ETnews_news_data.row_factory=sqlite3.Row
    ETnews_news_data.execute('create table if not exists ETnews(time TEXT,title TEXT,content TEXT, url TEXT UNIQUE);')
    ETnews_news_data.commit()

def Go_inside_page():       #網頁裡的東西 
    driver=webdriver.Chrome(drive_path)
    driver.implicitly_wait(3)
    driver.get('http://www.ettoday.net/news/news-list.htm')
    for i in range(70):
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(1)
    soup = BeautifulSoup(driver.page_source,'html.parser')
    for news in soup.select('.part_list_2'):
        for anews in news.select('h3'):
            ETnews_news_urls = anews.select('a')[0]['href']
            if (ETnews_news_urls.startswith("http://www.ettoday.net")==True):
                Add_news_item(ETnews_news_urls)
            else:
                ETnews_news_urls = domain + anews.select('a')[0]['href']
                Add_news_item(ETnews_news_urls)
    driver.close()
                
def Add_news_item(ETnews_news_urls):
    time.sleep(1)
    ETnews_news_data.row_factory=sqlite3.Row
    ETnews_news_content=''
    res=requests.get(ETnews_news_urls)
    soup = BeautifulSoup(res.text,'html.parser')
    if((soup.find('span',attrs={"class": "news-time"})) == None):   #時間
        for news_time in soup.select('.date'):  
            ETnews_news_time = re.sub('[^0-9年日月: -/]', "",news_time.text)          
    else:
        for news_time in soup.select('.news-time'):
            ETnews_news_time = re.sub('[^0-9年日月: -/]', "",news_time.text)    
    if ((soup.find('h1',attrs={"class": "title_article"}))==None):                
        ETnews_news_title = soup.select('.title')[0].text #標題
    else:
        ETnews_news_title = soup.select('.title_article')[0].text
    for news_content in soup.select('p'):           #文章
        ETnews_news_content += news_content.text
    
    Get_news_item(ETnews_news_time, ETnews_news_title, ETnews_news_content,ETnews_news_urls)
    ETnews_news_data.commit()
    
    
def Get_news_item(time,title,content,url):  
    ETnews_news_data.row_factory=sqlite3.Row
    ETnews_news_data.execute('insert or ignore into ETnews(time,title,content,url) values(?,?,?,?) ',(time,title,content,url)) #資料庫裡的文件
    ETnews_news_data.commit()


if __name__ == '__main__':main()
