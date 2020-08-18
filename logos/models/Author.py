# dependency
from mongoengine import *

# models
from logos.models.News import *


class Author(Document):
    agency_name = StringField(required=True)
    agency_url = StringField()
    news = ListField(ReferenceField(News), default=[])
