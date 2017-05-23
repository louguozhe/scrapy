# -*- coding: utf-8 -*-


import scrapy
import chardet

from hudongbaike.items import DriectoryItem
from hudongbaike.items import WordItem


#参考
#https://github.com/lawlite19/PythonCrawler-Scrapy-Mysql-File-Template

#CSS and XPath
#house_li = response.css('.house-lst .info-panel')
#house_li = response.xpath('//ul[@class="house-lst"]/li/div[@class="info-panel"]')
#response.css('.secondcon.fl li:nth-child(1)').css('.botline a::text').extract_first()
#response.xpath('//div[@class="secondcon fl"]//li[1]/span[@class="botline"]//a/text()').extract_first()
#response.css('.secondcon.fl li:last-child').css('.botline strong::text').extract_first()
#response.xpath('//div[@class="secondcon fl"]//li[last()]//span[@class="botline"]/strong/text()').extract_first()
#house_li.css('a::attr("href")').extract_first()
#house_li.xpath('.//a/@href').extract_first()

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

        yield scrapy.Request(response.urljoin(u'http://fenlei.baike.com/水果/'), callback=self.parse_ddindex)
        #yield scrapy.Request(response.urljoin(u'http://fenlei.baike.com/水果/list'), callback=self.parse_wordlist)
        #yield scrapy.Request(response.urljoin(u'http://www.baike.com/wiki/澳芒'), callback=self.parse_word)

    def parse_ddindex(self, response):

        ddname = response.xpath('//span[@id="category_title"]/text()').extract_first()
        item = DriectoryItem()
        item['name'] = ddname
        alist = response.css('div.sort_all p:nth-child(2) a::text').extract()
        item['parentnames'] = ','.join(alist)
        alist = response.css('div.sort_all p:nth-child(4) a::text').extract()
        item['sonnames'] = ','.join(alist)
        alist = response.css('div.sort_all p:nth-child(6) a::text').extract()
        item['relatednames'] = ','.join(alist)
        description = response.css('p.s2::text').extract()
        item['description'] = description
        yield item

        wordlist_url = response.css('span.h2_m > a:nth-child(2) ::attr(href)').extract_first()
        if wordlist_url:
            yield scrapy.Request(response.urljoin(wordlist_url), callback=self.parse_wordlist)

    def parse_wordlist(self, response):
        wordurllist = response.css('#all-sort > dl > dd')
        for word in wordurllist:
            wordurl = word.css('a::attr("href")').extract_first()
            yield scrapy.Request(response.urljoin(wordurl), callback=self.parse_word)
        pass

    def parse_word(self, response):
        item = WordItem()
        item['name'] = response.css('div.content-h1 > h1 ::text').extract_first()
        item['description'] = response.css('#anchor > p ::text').extract_first()
        yield item

    def parse(self, response):
        for dd in response.css('dd'):
            ddname = dd.css('a ::text').extract_first().encode('utf-8')
            yield {'dd': ddname}
            self.logger.info('A fenlei: %s', ddname)
        #for dd in response.xpath('//*[@id="f-a"]/div/div/dl/dd'):
        #    yield {'dd': dd.css('a ::text').extract_first()}

        #next_page = response.css('div.prev-post > a ::attr(href)').extract_first()
        #if next_page:
        #    yield scrapy.Request(response.urljoin(next_page), callback=self.parse)
