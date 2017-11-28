# -*- coding: utf-8 -*-
import scrapy

from baike.items import DirectoryItem
from baike.items import DirectoryGraphyItem
from baike.items import DirectoryRelationItem
from baike.items import WordItem


class BaidubaikeSpider(scrapy.Spider):
    name = 'baidubaike'
    allowed_domains = ['baike.baidu.com']
    #start_urls = ['http://fenlei.baike.com/']

    # def __init__(self, category=None, *args, **kwargs):
    #     super(FenleiSpider, self).__init__(*args, **kwargs)
        # if category:
        #     self.start_urls = ['http://www.example.com/categories/%s' % category]

    def start_requests(self):
        # instead start_urls
        #yield scrapy.Request('http://fenlei.baike.com/', self.parse_index)
        yield scrapy.Request(u'http://baike.baidu.com/fenlei/军事家', callback=self.parse_ddindex)

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

        yield scrapy.Request(response.urljoin(u'http://fenlei.baike.com/水果种类/'), callback=self.parse_ddindex)
        #yield scrapy.Request(response.urljoin(u'http://fenlei.baike.com/水果/list'), callback=self.parse_wordlist)
        #yield scrapy.Request(response.urljoin(u'http://www.baike.com/wiki/澳芒'), callback=self.parse_word)

    def parse_ddindex(self, response):
        # directory info
        ddname = response.css('div.g-row.bread.log-set-param > h3 ::text').extract_first().strip()
        item = DirectoryItem()
        item['name'] = ddname
        item['url'] = response.url
        #item['description'] = response.css('p.s2::text').extract_first().strip()
        yield item
        # sub directory
        sublist = response.css('div.g-row.p-category.log-set-param > div.category-title > a')
        for subname in sublist:
            subnamestr = subname.css('::text').extract_first().strip()
            item = DirectoryGraphyItem()
            item['name'] = ddname
            item['subname'] = subnamestr
            yield item
            subdirectoryurl = subname.css('::attr(href)').extract_first()
            yield scrapy.Request(response.urljoin(subdirectoryurl), callback=self.parse_ddindex)

        relationlist = response.css('div.g-row.p-category.log-set-param > div.brother-list > div > a')
        for relationname in relationlist:
            relationnamestr = relationname.css('::text').extract_first().strip()
            item = DirectoryRelationItem()
            item['name'] = ddname
            item['relationname'] = relationnamestr
            yield item

        print('debug>>>>>>> OK')
        wordurllist = response.css('div.grid-list.grid-list-spot > ul > li > div.list > a')
        for word in wordurllist:
            wordurl = word.css('::attr("href")').extract_first()
            yield scrapy.Request(response.urljoin(wordurl), callback=self.parse_word)
        pass

        # page
        pagelist = response.css('#pageIndex > a')
        yield [scrapy.Request(response.urljoin(pageurl), callback=self.parse_wordlist) for pageurl in pagelist]

    def parse_wordlist(self, response):
        print('debug>>>>>>> OK2')
        wordurllist = response.css('div.grid-list.grid-list-spot > ul > li > div.list > a')
        for word in wordurllist:
            wordurl = word.css('::attr("href")').extract_first()
            yield scrapy.Request(response.urljoin(wordurl), callback=self.parse_word)
        pass

        # page
        pagelist = response.css('#pageIndex > a')
        yield [scrapy.Request(response.urljoin(pageurl), callback=self.parse_wordlist) for pageurl in pagelist]

    def parse_word(self, response):
        item = WordItem()
        item['name'] = response.css('dl.lemmaWgt-lemmaTitle.lemmaWgt-lemmaTitle- > dd > h1 ::text').extract_first().strip()
        item['url'] = response.url
        descriptiontag = response.css('div.lemma-summary')
        item['description'] = ''
        if len(descriptiontag)>=1:
            item['description'] = descriptiontag[0].xpath('string(.)').extract_first()
        else: #可能为多义词
            pass
        yield item
