# http://doc.scrapy.org/en/latest/topics/items.html
from scrapy.item import Item, Field


class Media(Item):
    photographer = Field()
    url = Field()
    caption = Field()


class Article(Item):
    url = Field()
    title = Field()
    deck = Field()
    lead = Field()
    body = Field()
    authors = Field()
    media = Field()
    date = Field()
    section = Field()
    latitude = Field()
    longitude = Field()
    publication_date = Field()
