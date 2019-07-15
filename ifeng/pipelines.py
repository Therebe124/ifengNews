# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql

class IfengPipeline(object):
    def __init__(self):
      
        #self.conn = pymysql.connect(**dbparams)

        #sql表中 主键=number 唯一索引origin_url
        self.conn = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='123456',db='ifeng',charset='utf8')
        self.cursor = self.conn.cursor()
        self._sql = None

    def process_item(self, item, spider):
        self.cursor.execute(self.sql,(item['time'],item['title'],item['content'],item['url'],item['img'],item['img_details']))
        self.conn.commit()
        return item

    @property
    def sql(self):
        if not self._sql:
            self._sql ="""insert into article(number,pub_time,title,content,origin_url,img,img_details) values (null,%s,%s,%s,%s,%s,%s)"""
            return self._sql
        return self._sql
