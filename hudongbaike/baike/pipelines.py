# -*- coding: utf-8 -*-

import scrapy
import re
import datetime

from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
import codecs
import json
from baike.items import ConceptItem
from baike.items import ConceptRelationItem
from baike.items import DirectoryRelationItem
from baike.items import InstanceItem
from baike.items import InstanceDescriptionItem


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

re_kuohao1 = re.compile('\(.*\)')
re_kuohao2 = re.compile('\（.*\）')
constDateType_xsd_t = ' rdf:datatype="http://www.w3.org/2001/XMLSchema#%s"'
constDateType_string = constDateType_xsd_t % 'string'
constDateType_default = constDateType_string
constDateType_dataTime = constDateType_xsd_t % 'dateTime'

class OntologyPipeline:
    fenleiuri = 'http://fenlei.baike.com/ontology'
    ontofilename = 'directory.owl'
    graphyfilename = 'graphy.owl'
    propertyNameMap = {'0-100km/h加速时间':'百公里加速时间'}
    propertyTypeMap = {'出生日期':constDateType_dataTime,
                       '去世日期':constDateType_dataTime}
    def __init__(self):
        pass
    def open_spider(self, spider):
        self.dfile = codecs.open(self.ontofilename, 'w', encoding='utf-8')#保存为json文件
        self.dfile.write('<?xml version="1.0" encoding="utf-8" ?>\n')
        self.dfile.write('<rdf:RDF xmlns="%s#"\n' % self.fenleiuri)
        self.dfile.write('\txml:base="%s"\n' % self.fenleiuri)
        self.dfile.write('\txmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n')
        self.dfile.write('\txmlns:owl="http://www.w3.org/2002/07/owl#"\n')
        self.dfile.write('\txmlns:xml="http://www.w3.org/XML/1998/namespace"\n')
        self.dfile.write('\txmlns:xsd="http://www.w3.org/2001/XMLSchema#"\n')
        self.dfile.write('\txmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">\n')
        self.dfile.write('\t<owl:Ontology rdf:about="%s"/>\n' % self.fenleiuri)
        self.dfile.write('\t\n')
        self.dfile.write('\t\n')
        self.wfile = codecs.open(self.graphyfilename, 'w', encoding='utf-8')  # 保存为json文件
        self.wfile.write('name,property,value\n')  # 写入文件中

    def close_spider(self, spider):#爬虫结束时关闭文件
        self.dfile.write('</rdf:RDF>\n')
        self.dfile.close()
        self.wfile.close()

    def process_item(self, item, spider):
        if isinstance(item, ConceptItem):
            self.dfile.write('\t<owl:Class rdf:about="%s#%s">\n'% (self.fenleiuri,item['name']))
            self.dfile.write('\t\t<rdfs:isDefinedBy>%s</rdfs:isDefinedBy>\n'% (item['url']))
            self.dfile.write('\t</owl:Class>\n')
            pass
        elif isinstance(item, ConceptRelationItem):
            self.dfile.write('\t<owl:Class rdf:about="%s#%s">\n'% (self.fenleiuri,item['subname']))
            self.dfile.write('\t\t<rdfs:subClassOf rdf:resource="%s#%s"/>\n' % (self.fenleiuri,item['name']))
            self.dfile.write('\t</owl:Class>\n')
            #self.dfile.write('DirectoryGraphyItem->%s:%s\n' % (item['name'],item['subname']))  # 写入文件中
            pass
        elif isinstance(item, DirectoryRelationItem):
            #self.dfile.write('DirectoryRelationItem->%s:%s\n' % (item['name'],item['relationname']))  # 写入文件中
            pass
        elif isinstance(item, InstanceItem):
            realName = self.process_InstanceName(item['name'])
            if realName:
                self.dfile.write('\t<owl:NamedIndividual rdf:about = "%s#%s">\n' % (self.fenleiuri,realName))  # 写入文件中
                self.dfile.write('\t\t<rdf:type rdf:resource="%s#%s"/>\n' % (self.fenleiuri,item['type']))  # 写入文件中
                self.dfile.write('\t</owl:NamedIndividual>\n')  # 写入文件中
        elif isinstance(item, InstanceDescriptionItem):
            realName = self.process_InstanceName(item['name'])
            realPropertyName = self.process_propertyName(item['property'])
            if realPropertyName:
                self.dfile.write('\t<owl:NamedIndividual rdf:about = "%s#%s">\n' % (self.fenleiuri, realName))  # 写入文件中
                realPropertyType = self.process_propertyType(realPropertyName)
                realPropertyValue = self.process_propertyValue(realPropertyType,item['value'])
                self.dfile.write('\t\t<%s%s>%s</%s>\n' % (realPropertyName,realPropertyType,realPropertyValue,realPropertyName))  # 写入文件中
                self.dfile.write('\t</owl:NamedIndividual>\n')  # 写入文件中
                self.wfile.write('%s,%s,%s\n' % (item['name'],realPropertyName,realPropertyValue))  # 写入文件中
            pass
        return item

    def process_InstanceName(self,instanceName):
        if instanceName:
            instanceName = instanceName.replace(' ', '').replace(' ', '')
        return instanceName

    def process_propertyName(self,propertyName):
        if propertyName:
            propertyName = propertyName.replace('：', '').replace(' ', '').replace(' ', '').replace('/', '').replace('、', '')
        propertyName = re_kuohao1.sub('',propertyName)
        propertyName = re_kuohao2.sub('',propertyName)
        propertyName = self.propertyNameMap.get(propertyName,propertyName)
        if len(propertyName)>0 and propertyName[0].isdigit():
            return None
        return propertyName

    def process_propertyType(self,propertyName):
        return self.propertyTypeMap.get(propertyName,constDateType_default)

    def process_propertyValue(self,propertyType,propertyValue):
        if propertyValue:
            propertyValue = propertyValue.replace('\n','').replace('  ','')
            if propertyType == constDateType_dataTime:
                try:
                    if '-' in propertyValue:
                        dateValue = datetime.datetime.strptime(propertyValue, "%Y-%m-%d")
                    elif '年' in propertyValue:
                        dateValue = datetime.datetime.strptime(propertyValue, "%Y年%m月%d日")
                    return dateValue.strftime('%Y-%m-%d')
                except Exception as e:
                    print(e)
                    return '1900-01-01'
        return propertyValue

class HudongOntologyPipeline(OntologyPipeline):
    def __init__(self):
        self.fenleiuri = 'http://fenlei.hudong.com/ontology'
        self.ontofilename = 'hudong_fenlei.owl'
        self.graphyfilename = 'hudong_graphy.owl'

class BaiduOntologyPipeline(OntologyPipeline):
    def __init__(self):
        self.fenleiuri = 'http://fenlei.baidu.com/ontology'
        self.ontofilename = 'baidu_fenlei.owl'
        self.graphyfilename = 'baidu_graphy.owl'


class HudongbaikePipeline(object):
    '''保存到数据库中对应的class
       1、在settings.py文件中配置
       2、在自己实现的爬虫类中yield item,会自动执行'''

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        '''1、@classmethod声明一个类方法，而对于平常我们见到的则叫做实例方法。
           2、类方法的第一个参数cls（class的缩写，指这个类本身），而实例方法的第一个参数是self，表示该类的一个实例
           3、可以通过类来调用，就像C.f()，相当于java中的静态方法'''
        dbparams = dict(
            host=settings['MYSQL_HOST'],  # 读取settings中的配置
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',  # 编码要加上，否则可能出现中文乱码问题
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=False,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams)  # **表示将字典扩展为关键字参数,相当于host=xxx,db=yyy....
        return cls(dbpool)  # 相当于dbpool付给了这个类，self中可以得到

    # pipeline默认调用
    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self._conditional_insert, item)  # 调用插入的方法
        query.addErrback(self._handle_error, item, spider)  # 调用异常处理方法
        return item

    # 写入数据库中
    def _conditional_insert(self, tx, item):
        if isinstance(item, DirectoryItem):
            sql = "insert into hudong_directory_description(name,url,description) values(%s,%s,%s)"
            params = (item['name'],item['url'], item['description'])
            tx.execute(sql, params)
        elif isinstance(item, DirectoryGraphyItem):
            sql = "insert into hudong_directory_graphy(name,subname) values(%s,%s)"
            params = (item['name'], item['subname'])
            tx.execute(sql, params)
        elif isinstance(item, DirectoryRelationItem):
            sql = "insert into hudong_directory_relation(name,relationname) values(%s,%s)"
            params = (item['name'], item['relationname'])
            tx.execute(sql, params)
        elif isinstance(item, WordItem):
            sql = "insert into hudong_word_description(name,description,url) values(%s,%s,%s)"
            params = (item['name'], item['description'], item['url'])
            tx.execute(sql, params)

            #tx.commit()

    # 错误处理方法
    def _handle_error(self, failue, item, spider):
        print('--------------database operation exception!!-----------------')
        print('-------------------------------------------------------------')
        print(failue)