# -*- coding: utf-8 -*-


import scrapy
import urllib.parse
from baike.items import ConceptItem
from baike.items import ConceptRelationItem
from baike.items import DirectoryRelationItem
from baike.items import InstanceItem
from baike.items import InstanceDescriptionItem


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

class HudongbaikeSpider(scrapy.spiders.Spider):
    name = 'hudongbaike'
    allowed_domains = ['baike.com']

    def start_requests(self):
        #yield scrapy.Request(u'http://fenlei.baike.com/页面总分类', callback=self.parse_treeindex)
        #yield scrapy.Request(u'http://fenlei.baike.com/军事', callback=self.parse_ddindex)
        yield scrapy.Request(u'http://fenlei.baike.com/中国革命烈士', callback=self.parseConceptIndex)

    #解析概念页
    def parseConceptIndex(self, response):
        # 概念名称
        ddname = response.css('div.f_2-app > ul > li > h5 ::text').extract_first()
        if ddname == None:
            return
        item = ConceptItem()
        item['name'] = ddname
        item['url'] = response.url
        yield item
        # 上下级概念信息
        taghs = response.css('div.f_2 div:nth-child(2) h3')
        i = 1
        for tagh in taghs:
            tag = tagh.css('::text').extract_first().strip()
            if tag == u'上一级微百科':
                pass
            elif tag == u'下一级微百科':
                sublist = response.css('div.f_2 div:nth-child(2) p:nth-child(%d) a' % (i*2))
                for subname in sublist:
                    subnamestr = subname.css('::text').extract_first().strip()
                    #subnamestr = urllib.parse.unquote(subdirectoryurl.split('/')[-1])
                    item = ConceptRelationItem()
                    item['name'] = ddname
                    item['subname'] = subnamestr
                    yield item
                    subdirectoryurl = subname.css('::attr(href)').extract_first()
                    yield scrapy.Request(subdirectoryurl, callback=self.parseConceptIndex)
            i = i + 1

       # 实例列表分页
        wordlist_url = response.css('span.h2_m > a:nth-child(2) ::attr(href)').extract_first()
        if wordlist_url:
            yield scrapy.Request(response.urljoin(wordlist_url), callback=self.parseInstanceList)

    # 分析实例列表
    def parseInstanceList(self, response):
        typename=urllib.parse.unquote(str(response.url).split('/')[-3])
        wordurllist = response.css('#all-sort > dl > dd')
        for word in wordurllist:
            wordname = urllib.parse.unquote(word.css('a::attr(href)').extract_first().split('/')[-1]).replace('　','').replace('"','-').replace('&quot;','').replace('--','-')
            if wordname == "javascript:void(0);":
                continue
            #wordname = word.css('a::text').extract_first()
            wordurl = word.css('a::attr("href")').extract_first()
            item = InstanceItem()
            item['name'] = wordname
            item['type'] = typename
            item['url'] = wordurl
            yield item
            yield scrapy.Request(response.urljoin(wordurl), callback=self.parseInstance)
        pass

    # 解析实例
    def parseInstance(self, response):
        #实例名
        wordname = response.css('div.content-h1 > h1 ::text').extract_first().strip()
        #实例属性
        #print('debug: %s %d' % (wordname,len(response.css('#datamodule > div > table > tr'))))
        infos = response.css('#datamodule > div > table > tr')
        for info in infos:
            property = info.css('td:nth-child(1) strong ::text').extract_first()
            if property:
                item = InstanceDescriptionItem()
                item['name'] = wordname
                item['property'] = property.replace('：','')
                item['value'] = info.css('td:nth-child(1) span').xpath('string(.)').extract_first().replace('\n','').replace('  ','')
                yield item
            property = info.css('td:nth-child(3) strong ::text').extract_first()
            if property:
                item = InstanceDescriptionItem()
                item['name'] = wordname
                item['property'] = property.replace('：','')
                item['value'] = info.css('td:nth-child(3) span').xpath('string(.)').extract_first().replace('\n','').replace('  ','')
                yield item
        #实例描述
        #item['description'] = response.css('#anchor > p ::text').extract_first()
        # descriptiontag = response.css('#anchor > p')
        # item['description'] = ''
        # if len(descriptiontag)>=1:
        #     item['description'] = descriptiontag[0].xpath('string(.)').extract_first()
        # yield item
