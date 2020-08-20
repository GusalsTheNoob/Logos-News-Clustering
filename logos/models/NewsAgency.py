# dependency
from mongoengine import *

# models
from logos.models.News import *
from logos.models.Author import *


class NewsAgency(Document):
    agency_name = StringField(required=True)
    agency_url = StringField(primary_key=True, required=True, min_length=1)
    agency_thumbnail = StringField(min_length=1)
    news = ListField(ReferenceField(News), default=[])
    authors = ListField(ReferenceField(Author), default=[])
