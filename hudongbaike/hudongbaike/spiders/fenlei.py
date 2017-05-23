# -*- coding: utf-8 -*-
import scrapy


class FenleiSpider(scrapy.Spider):
    name = 'fenlei'
    allowed_domains = ['http://fenlei.baike.com/']
    start_urls = ['http://http://fenlei.baike.com//']

    def parse(self, response):
        pass
