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
        target_url = self.__target_url + \
            f"&page={page}" + \
            f"&date={datetime_to_datestamp(target_date)}"
        news_docs, page_num = self.__get_news_headers(target_url)
        updated_news_docs = self.__get_news_contents(news_docs)
        if page_num == page:  # if there's more page
            return self.crawl(page=page+1, target_date=target_date) + updated_news_docs
        else:
            return updated_news_docs

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
        news_docs = list(filter(lambda x: x is not None,
                                map(self.__parse_and_save_header, row_soups)))
        return news_docs

    def __parse_and_save_header(self, row_soup):
        news_url = trimNewsURL(row_soup.find('a')['href'])
        ## duplicacy check ##
        if News.objects(news_url=news_url).count() > 0:
            return None
        #####################
        news_doc = News(
            news_type=f"naver/0.0.0",
            news_url=news_url,
            metadata=NewsMetaData(),
            content=NewsContent(
                title=row_soup.find("a").string.strip()
            )
        )
        news_doc.save()
        return news_doc

    def __parse_pagenum(self, pagebar_soup):
        return int(pagebar_soup.find("strong").string)

    def __get_news_contents(self, news_docs):
        updated_news_docs = list(map(self.__get_news_content, news_docs))
        return updated_news_docs

    def __get_news_content(self, news_doc):
        target_url = convert_to_mobile(news_doc.news_url)
        header_soup, main_soup = self.__retrieve_content(target_url)
        updated_news_doc = self.__parse_and_save_content(
            news_doc.news_url, header_soup, main_soup)
        return updated_news_doc

    def __retrieve_content(self, target_url):
        self.__driver.get(target_url)
        time.sleep(2)
        header_strainer = SoupStrainer(
            'div', {'class': 'media_end_head go_trans'})
        header_soup = bs(self.__driver.page_source,
                         features='lxml', parse_only=header_strainer)
        main_strainer = SoupStrainer('div', {'class': 'newsct_article'})
        main_soup = bs(self.__driver.page_source,
                       features='lxml', parse_only=main_strainer)
        return header_soup, main_soup

    def __parse_and_save_content(self, news_url, header_soup, main_soup):
        current_news_doc = News.objects(news_url=news_url)[0]
        # parsing content
        current_news_doc.content.content = main_soup.text
        current_news_doc.content.title = header_soup.find(
            'h2', {'class': 'media_end_head_headline'}).string
        # parsing channel
        channel_dict = {
            'channel_name': header_soup.find(
                'img', {'class': 'media_end_head_top_logo_img'})['title'],
            'channel_href':  header_soup.find(
                'a', {'class': 'media_end_head_top_logo'})['href'],
            'channel_thumbnail': header_soup.find(
                'img', {'class': 'media_end_head_top_logo_img'})['src']
        }
        channel_doc = self.__fetch_channel(channel_dict)
        current_news_doc.metadata.channel_name = channel_dict['channel_name']
        current_news_doc.metadata.channel_id = channel_doc.agency_url
        # parsing author
        author_docs = []
        for part in header_soup.findAll('a', {'class': 'media_end_head_journalist_layer_link _like_cheer_count _LIKE_HIDE'}):
            author_dict = {
                'author_name':  re.sub(" 기자", "", part.find('em', {'class': 'media_end_head_journalist_layer_name'}).string),
                'author_href': "/".join(part['href'].split("/")[-2:])
            }
            author_docs.append(self.__fetch_author(author_dict, channel_dict))
        current_news_doc.metadata.author_names = [
            author_doc.author_name for author_doc in author_docs]
        current_news_doc.metadata.author_ids = [
            author_doc.author_id for author_doc in author_docs]
        # parsing time
        time_str = header_soup.find('span', {
                                    'class': 'media_end_head_info_datestamp_time _ARTICLE_DATE_TIME'})['data-date-time']
        current_news_doc.metadata.uploaded_at = datetime.strptime(
            time_str, '%Y-%m-%d %H:%M:%S')
        # filling in references
        channel_doc.news.append(current_news_doc)
        for author_doc in author_docs:
            channel_doc.authors.append(author_doc)
            author_doc.news.append(current_news_doc)
        return current_news_doc

    def __fetch_channel(self, channel_dict):
        channel_query = NewsAgency.objects(
            agency_url=channel_dict["channel_href"])
        if channel_query.count() == 0:
            agency_doc = NewsAgency(
                agency_name=channel_dict["channel_name"],
                agency_url=channel_dict["channel_href"],
                agency_thumbnail=channel_dict["channel_thumbnail"]
            )
            agency_doc.save()
        else:
            agency_doc = channel_query[0]
        return agency_doc

    def __fetch_author(self, author_dict, channel_dict):
        author_query = Author.objects(author_id=author_dict["author_href"])
        if author_query.count() == 0:
            author_doc = Author(
                author_id=author_dict["author_href"],
                author_name=author_dict["author_name"],
                agency_url=channel_dict["channel_href"],
                agency_name=channel_dict["channel_name"]
            )
            author_doc.save()
        else:
            author_doc = author_query[0]
        return author_doc

    def close_driver(self):
        self.__driver.close()
