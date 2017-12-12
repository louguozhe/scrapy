# -*- coding: utf-8 -*-
import scrapy

from baike.items import ConceptItem
from baike.items import ConceptRelationItem
from baike.items import DirectoryRelationItem
from baike.items import InstanceItem
from baike.items import InstanceDescriptionItem

class BaidubaikeSpider(scrapy.Spider):
    name = 'baidubaike'
    allowed_domains = ['baike.baidu.com']

    def start_requests(self):
        # instead start_urls
        #yield scrapy.Request('http://fenlei.baike.com/', self.parse_index)
        #yield scrapy.Request(u'http://baike.baidu.com/fenlei/军事', callback=self.parseConceptIndex)
        #yield scrapy.Request(u'http://baike.baidu.com/fenlei/军事家', callback=self.parseConceptIndex)
        #yield scrapy.Request(u'http://baike.baidu.com/fenlei/革命家', callback=self.parseConceptIndex)
        yield scrapy.Request(u'http://baike.baidu.com/fenlei/军事学', callback=self.parseConceptIndex)

    #概念主页
    def parseConceptIndex(self, response):
        # directory info
        ddname = response.css('div.g-row.bread.log-set-param > h3 ::text').extract_first()
        if ddname == None:
            return
        item = ConceptItem()
        item['name'] = ddname
        item['url'] = response.url
        #item['description'] = response.css('p.s2::text').extract_first().strip()
        yield item
        # sub directory
        sublist = response.css('div.g-row.p-category.log-set-param > div.category-title > a')
        print('debug: %d' % len(sublist))
        for subname in sublist:
            subnamestr = subname.css('::text').extract_first().strip()
            item = ConceptRelationItem()
            item['name'] = ddname
            item['subname'] = subnamestr
            yield item
            subdirectoryurl = subname.css('::attr(href)').extract_first()
            yield scrapy.Request(response.urljoin(subdirectoryurl), callback=self.parseConceptIndex)

        relationlist = response.css('div.g-row.p-category.log-set-param > div.brother-list > div > a')
        for relationname in relationlist:
            relationnamestr = relationname.css('::text').extract_first().strip()
            item = DirectoryRelationItem()
            item['name'] = ddname
            item['relationname'] = relationnamestr
            yield item

        wordurllist = response.css('div.grid-list.grid-list-spot > ul > li > div.list > a')
        for word in wordurllist:
            #wordurl = word.css('::attr("href")').extract_first()
            #yield scrapy.Request(response.urljoin(wordurl), callback=self.parse_word)
            wordname = word.css('::text').extract_first()
            item = InstanceItem()
            item['name'] = wordname
            item['type'] = ddname
            yield item
        pass

        # page
        pagelist = response.css('#pageIndex > a')
        for pageurl in pagelist:
            yield scrapy.Request(response.urljoin(pageurl.css('::attr("href")').extract_first()), callback=self.parse_wordlist)

    #解析实体列表
    def parse_wordlist(self, response):
        wordurllist = response.css('div.grid-list.grid-list-spot > ul > li > div.list > a')
        ddname = response.css('div.g-row.bread.log-set-param > h3 ::text').extract_first()
        for word in wordurllist:
            wordname = word.css('::text').extract_first()
            wordurl = word.css('::attr("href")').extract_first()
            item = InstanceItem()
            item['name'] = wordname
            item['type'] = ddname
            item['url'] = wordurl
            yield item
            yield scrapy.Request(response.urljoin(wordurl), callback=self.parse_word)
        pass
        # page
        pagelist = response.css('#pageIndex > a')
        for pageurl in pagelist:
            yield scrapy.Request(response.urljoin(pageurl.css('::attr("href")').extract_first()), callback=self.parse_wordlist)

    def parse_word(self, response):
        wordName = response.css('dl.lemmaWgt-lemmaTitle.lemmaWgt-lemmaTitle- > dd > h1 ::text').extract_first()
        if wordName:
            wordName = wordName.strip()
        basicInfoNames = response.css('dl.basicInfo-block:nth-child(1) > dt')
        #print('debug: %s %d' % (wordName,len(basicInfoNames)))
        index = 1
        for basicInfoName in basicInfoNames:
            item = InstanceDescriptionItem()
            item['name'] = wordName
            item['property'] = basicInfoName.css('::text').extract_first().replace(' ','')
            item['value'] = response.css('dl.basicInfo-block:nth-child(1) > dd:nth-child(%d) ::text' % (2*index)).extract_first().replace('\n','')
            yield item
            index = index + 1
        # descriptiontag = response.css('div.lemma-summary')
        # item['description'] = ''
        # if len(descriptiontag)>=1:
        #     item['description'] = descriptiontag[0].xpath('string(.)').extract_first()
        # else: #可能为多义词
        #     pass
        # yield item
