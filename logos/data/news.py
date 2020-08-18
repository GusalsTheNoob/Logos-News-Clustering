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

    def close_driver(self):
        self.__driver.close()
