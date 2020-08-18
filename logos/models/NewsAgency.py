# dependency
from mongoengine import *

# models
from logos.models.News import *
from logos.models.Author import *


class NewsAgency(Document):
    agency_name = StringField(required=True)
    agency_url = StringField()
    news = ListField(ReferenceField(News), default=[])
    authors = ListField(ReferenceField(Author), default=[])
