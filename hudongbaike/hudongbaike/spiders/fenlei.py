# -*- coding: utf-8 -*-
import scrapy

from hudongbaike.items import DriectoryItem


#参考
#https://github.com/lawlite19/PythonCrawler-Scrapy-Mysql-File-Template


class FenleiSpider(scrapy.Spider):
    name = 'fenlei'
    allowed_domains = ['baike.com']
    #start_urls = ['http://fenlei.baike.com/']

    # def __init__(self, category=None, *args, **kwargs):
    #     super(FenleiSpider, self).__init__(*args, **kwargs)
        # if category:
        #     self.start_urls = ['http://www.example.com/categories/%s' % category]

    def start_requests(self):
        # instead start_urls
        yield scrapy.Request('http://fenlei.baike.com/', self.parse_index)
        #yield scrapy.Request('http://www.example.com/2.html', self.parse)

    # def start_requests(self):
    #     return [scrapy.FormRequest("http://www.example.com/login",
    #                                formdata={'user': 'john', 'pass': 'secret'},
    #                                callback=self.logged_in)]
    #
    # def logged_in(self, response):
    #     # here you would extract links to follow and return Requests for
    #     # each of them, with another callback
    #     pass

    def parse_index(self, response):
        # for dd in response.css('dd'):
        #     ddurl = dd.css('a ::text').extract_first()
        #     yield scrapy.Request(response.urljoin(ddurl), callback=self.parse_ddindex)
        # pass
        yield scrapy.Request(response.urljoin(u'http://fenlei.baike.com/女性科学家/'), callback=self.parse_ddindex)

    def parse_ddindex(self, response):
        ddname = response.css('span#category_title ::text').extract_first()
        item = DriectoryItem()
        item['name'] = ddname
        parentnames = response.css('div.sort_all > p[1] > a::text').extract_first()
        item['parentnames'] = ''
        yield item


    def parse(self, response):
        for dd in response.css('dd'):
            ddname = dd.css('a ::text').extract_first()
            yield {'dd': ddname}
            self.logger.info('A fenlei: %s', ddname)
        #for dd in response.xpath('//*[@id="f-a"]/div/div/dl/dd'):
        #    yield {'dd': dd.css('a ::text').extract_first()}

        #next_page = response.css('div.prev-post > a ::attr(href)').extract_first()
        #if next_page:
        #    yield scrapy.Request(response.urljoin(next_page), callback=self.parse)
