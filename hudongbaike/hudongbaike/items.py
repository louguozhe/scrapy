# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DirectoryItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()
    pass

class DirectoryGraphyItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    subname = scrapy.Field()
    pass
class DirectoryRelationItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    relationname = scrapy.Field()
    pass

class WordItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    description = scrapy.Field()