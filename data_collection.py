# dependency
from datetime import datetime
from dotenv import load_dotenv
import os


# in-package references
from logos.data.news import NewsCollector
from logos.db import DB

# env params
load_dotenv(verbose=True)
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
NEWS_DB_NAME = os.getenv("NEWS_DB_NAME")


# Calling kernels
db = DB(HOST, PORT, NEWS_DB_NAME)
test_collector = NewsCollector(db)
test_collector.close_driver()
