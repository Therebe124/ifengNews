# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import redis
import pandas

#connect redis 
redis_db = redis.Redis(host='127.0.0.1',port=6379,db=4,password='123456')
redis_data_dict = 'u'

class IfengPipeline(object):
    def __init__(self):
      
        #self.conn = pymysql.connect(**dbparams)

        #sql表中 主键=number 唯一索引origin_url
        self.conn = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='123456',db='ifeng',charset='utf8')
        self.cursor = self.conn.cursor()
        self._sql = None

        redis_db.flushdb()
        if redis_db.hlen(redis_data_dict)==0:
            sql = 'select origin_url from article'
            df = pandas.read_sql(sql,self.conn)

            for url in df['origin_url'].get_values():
                redis_db.hset(redis_data_dict,url,0)
            

    def process_item(self, item, spider):
        if redis_db.hexists(redis_data_dict,item['url']):
            print("数据重复")
        else:
            self.cursor.execute(self.sql,(item['time'],item['title'],item['content'],item['url'],item['img'],item['img_details']))
            self.conn.commit()
        return item

    @property
    def sql(self):
        if not self._sql:
            self._sql ="""insert into article(number,pub_time,title,content,origin_url,img,img_details) values (null,%s,%s,%s,%s,%s,%s)"""
            return self._sql
        return self._sql

