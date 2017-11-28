# -*- coding: utf-8 -*-
import scrapy
from baike.items import WordItem

class TestspiderSpider(scrapy.Spider):
    name = "testspider"
    allowed_domains = ["baike.baidu.com"]
    start_urls = ['http://baike.baidu.com/item/永恒之石/20816991']

    def parse(self, response):
        item = WordItem()
        c = response.xpath('//div[@class="lemma-summary"]')
        d = c[0].xpath('string(.)').extract_first()
        item['name'] = d
        item['description'] = u''
        yield item
