# dependency
from mongoengine import *


class NewsMetaData(EmbeddedDocument):
    channel_id = StringField(min_length=1)
    channel_name = StringField(min_length=1)
    author_ids = ListField(StringField(min_length=1))
    author_names = ListField(StringField(min_length=1))
    uploaded_at = DateTimeField()


class NewsContent(EmbeddedDocument):
    title = StringField(required=True, min_length=1)
    content = StringField()


class News(Document):
    news_type = StringField(required=True)  # "youtube/0.0.0/video"
    news_url = StringField(required=True, primary_key=True, min_length=1)
    metadata = EmbeddedDocumentField(NewsMetaData)
    content = EmbeddedDocumentField(NewsContent)
