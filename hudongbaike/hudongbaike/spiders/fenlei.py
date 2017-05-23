# -*- coding: utf-8 -*-
import scrapy


class FenleiSpider(scrapy.Spider):
    name = 'fenlei'
    allowed_domains = ['fenlei.baike.com']
    start_urls = ['http://fenlei.baike.com/']

    def parse(self, response):
        for dd in response.css('dd'):
            yield {'dd': dd.css('a ::text').extract_first()}
        #for dd in response.xpath('//*[@id="f-a"]/div/div/dl/dd'):
        #    yield {'dd': dd.css('a ::text').extract_first()}

        #next_page = response.css('div.prev-post > a ::attr(href)').extract_first()
        #if next_page:
        #    yield scrapy.Request(response.urljoin(next_page), callback=self.parse)
