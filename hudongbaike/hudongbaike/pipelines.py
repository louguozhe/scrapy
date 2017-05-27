# -*- coding: utf-8 -*-

from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
import codecs
import json
import items

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

class JsonWithEncodingPipeline(object):
    '''保存到文件中对应的class
       1、在settings.py文件中配置
       2、在自己实现的爬虫类中yield item,会自动执行'''
    def __init__(self):
        self.dfile = codecs.open('directory.txt', 'w', encoding='utf-8')#保存为json文件
        self.wfile = codecs.open('word.txt', 'w', encoding='utf-8')  # 保存为json文件

    def process_item(self, item, spider):
        print('JsonWithEncodingPipeline.process_item: %s' % item['name'])
        if isinstance(item, items.DirectoryItem):
            self.dfile.write('DirectoryItem->%s:%s\n' % (item['name'],item['url']))  # 写入文件中
            pass
        elif isinstance(item, items.DirectoryGraphyItem):
            self.dfile.write('DirectoryGraphyItem->%s:%s\n' % (item['name'],item['subname']))  # 写入文件中
            pass
        elif isinstance(item, items.DirectoryRelationItem):
            self.dfile.write('DirectoryRelationItem->%s:%s\n' % (item['name'],item['relationname']))  # 写入文件中
            pass
        elif isinstance(item, items.WordItem):
            self.dfile.write('WordItem->%s:%s\n' % (item['name'],item['description']))  # 写入文件中
            pass
        return item
    def spider_closed(self, spider):#爬虫结束时关闭文件
        self.dfile.close()
        self.wfile.close()

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
        if isinstance(item, items.DirectoryItem):
            sql = "insert into hudong_directory_description(name,url,description) values(%s,%s,%s)"
            params = (item['name'],item['url'], item['description'])
            tx.execute(sql, params)
        elif isinstance(item, items.DirectoryGraphyItem):
            sql = "insert into hudong_directory_graphy(name,subname) values(%s,%s)"
            params = (item['name'], item['subname'])
            tx.execute(sql, params)
        elif isinstance(item, items.DirectoryRelationItem):
            sql = "insert into hudong_directory_relation(name,relationname) values(%s,%s)"
            params = (item['name'], item['relationname'])
            tx.execute(sql, params)
        elif isinstance(item, items.WordItem):
            sql = "insert into hudong_word_description(name,description) values(%s,%s)"
            params = (item['name'], item['description'])
            tx.execute(sql, params)

            #tx.commit()

    # 错误处理方法
    def _handle_error(self, failue, item, spider):
        print '--------------database operation exception!!-----------------'
        print '-------------------------------------------------------------'
        print failue