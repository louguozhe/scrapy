# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ConceptItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()
    pass

class ConceptRelationItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    subname = scrapy.Field()
    pass
class DirectoryRelationItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    relationname = scrapy.Field()
    pass

class InstanceItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    type = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()

class InstanceDescriptionItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    property = scrapy.Field()
    value = scrapy.Field()
    description = scrapy.Field()