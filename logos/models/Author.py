# dependency
from mongoengine import *

# models
from logos.models.News import *


class Author(Document):
    author_name = StringField(min_length=1)
    author_id = StringField(primary_key=True, required=True)
    agency_name = StringField(required=True)
    agency_url = StringField()
    news = ListField(ReferenceField(News), default=[])
