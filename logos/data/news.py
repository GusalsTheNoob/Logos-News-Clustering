# dependency
from bs4 import BeautifulSoup as bs
from bs4 import SoupStrainer
from datetime import datetime, timedelta
from itertools import chain
import logging
from mongoengine import *
from mongoengine.errors import ValidationError
import re
from selenium import webdriver
import time


# in-package references
# helper classes

from logos.db import DB
# models
from logos.models.News import *
from logos.models.Author import *
from logos.models.NewsAgency import *
# utilities
from logos.data.utilities import *


# news collection kernel
class NewsCollector:
    """
    # TODO: Fill in Class Doc
    """

    def __init__(self, db, target_url="https://news.naver.com/main/list.nhn?mode=LSD&sid1=001&mid=sec&listType=title"):
        self.__connect_to_DB(db)
        self.__initiate_driver()
        self.__target_url = target_url

    def __connect_to_DB(self, db):
        connect(db.get_DB_name(), host=db.get_DB_url())

    def __initiate_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        chrome_options.add_argument('Mozilla/5.0')
        self.__driver = webdriver.Chrome(
            'chromedriver', options=chrome_options)

    def crawl(self, page=1, target_date=datetime.now().date()):
        print(page)
        target_url = self.__target_url + \
            f"&page={page}" + \
            f"&date={datetime_to_datestamp(target_date)}"
        news_docs, page_num = self.__get_news_headers(target_url)
        if page_num == page:  # if there's more page
            self.crawl(page=page+1, target_date=target_date)

    def __get_news_headers(self, target_url):
        content_soup, pagebar_soup = self.__retrieve_headers(target_url)
        news_docs = self.__parse_and_save_headers(content_soup)
        page_num = self.__parse_pagenum(pagebar_soup)
        return news_docs, page_num

    def __retrieve_headers(self, target_url):
        self.__driver.get(target_url)
        self.__retrieved_time = datetime.now()
        time.sleep(1)
        content_strainer = SoupStrainer('ul', {'class': 'type02'})
        content_soup = bs(self.__driver.page_source,
                          features='lxml', parse_only=content_strainer)
        pagebar_strainer = SoupStrainer('div', {'class': 'paging'})
        pagebar_soup = bs(self.__driver.page_source, features='lxml',
                          parse_only=pagebar_strainer)
        return content_soup, pagebar_soup

    def __parse_and_save_headers(self, content_soup):
        row_soups = chain(*[table_soup.findAll("li")
                            for table_soup in content_soup])
        news_docs = list(map(self.__parse_and_save_header, row_soups))
        return news_docs

    def __parse_and_save_header(self, row_soup):
        news_url = trimNewsURL(row_soup.find('a')['href'])
        ## duplicacy check ##
        if News.objects(news_url=news_url).count() > 0:
            print("What?")
            return None
        #####################
        news_doc = News(
            news_type=f"naver/0.0.0",
            news_url=news_url,
            metadata=NewsMetaData(
                uploaded_at=ntimestamp_to_datetime(
                    row_soup.find("span", {"class": "date"}).string, self.__retrieved_time)
            ),
            content=NewsContent(
                title=row_soup.find("a").string.strip()
            )
        )
        news_doc.save()
        return news_doc

    def __parse_pagenum(self, pagebar_soup):
        return int(pagebar_soup.find("strong").string)

    def close_driver(self):
        self.__driver.close()
