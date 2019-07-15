# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ifeng.items import ArticleItem
import re
import os


class IfnewsSpider(CrawlSpider):
    name = 'ifnews'
    allowed_domains = ['news.ifeng.com']
    start_urls = ['http://news.ifeng.com/rt-channel/rtlist_0/index.shtml']


    restrict_xpath = '//div[@class="newsList"]'

    #http://news.ifeng.com/rt-channel/rtlist_20150408/1.shtml

    #根据不同规则，a/***,callback=parse_a   photo/*** , callback = parse_photo
    rules = (
        Rule(
            LinkExtractor(allow=r'.*/a/*',restrict_xpaths = restrict_xpath), callback='parse_a', follow=True
        ),
        Rule(
            LinkExtractor(allow=r'.*/rt-channel/*',restrict_xpaths = restrict_xpath), callback=None, follow=True
        ),
        Rule(
            LinkExtractor(allow=r'.*/photo/*',restrict_xpaths = restrict_xpath), callback='parse_photo', follow=True
        ),
    )
    #能抓取http://news.ifeng.com/rt-channel/rtlist_20150408/2.shtml
    #class='newsList'

    def parse_a(self, response):
        

        item = ArticleItem()

        #从html的head中获取time、title、url
        item['time'] = response.xpath('//head/meta[@name="og:time"]/@content').get()
        #item['time'] = response.xpath('//span[@class="ss01"]/text()').get()
        
        #title
        item['title'] = response.xpath('//head/meta[@property="og:title"]/@content').get()

        #item['title'] = response.xpath('//h1/text()').get()
        #item['title'] = response.xpath('//h1[@id="artical_topic"]/text()').get()      


        #对文章内容进行筛选和拼接
        content=""
        #提取出所有不含标签的内容，此内容为文章正文
        article = response.xpath('//div[@id="main_content"]/p[not(@*)]/text()')

        #社会话题，网页分布不一样，没有main_content
        if article:
            pass
            #item['img'] = response.xpath('//div[@id="main_content"]/p[@class="detailPic"]/img/@src').get()
        else:
            article = response.xpath('//div[@class="wrapIphone AtxtType01"]/p[not(@*)]/text()')
        #拼接<p>标签
        for p in article:
            content = content + p.extract().strip()
        content = '%s %s %s' % ('<p>',content,'</p>')

        item['content'] =content

        #img
        photo = response.xpath('//div[@id="main_content"]/p[@class="detailPic"]/img/@src')
        img = ''
        if photo:
            for p in photo:
                img = img + "'" + p.extract().strip() + "'"
        else:
            pass   

        item['img'] = img
        #img_details
        details = response.xpath('//div[@id="main_content"]/p[@class="picIntro"]/span/text()')
        img_details = ''
        if details:
            for p in details:
                img_details = img_details + "'" + p.extract().strip() + "'"
        else:
            pass

        item['img_details'] = img_details

        #url
        #item['url'] = response.xpath('//head/meta[@property="og:url"]/@content').get()
        item['url'] = response.url

      
        yield item

    #组图情况下
    def parse_photo(self, response):
        item = ArticleItem()
        item['time']=response.xpath('//h4/text()').get()
        item['title'] =response.xpath('//h1/text()').get()
        
        #item['content'] =response.xpath('//p[@id="photoDesc"]/text()').get()
        item['content']=""
       
        #从<script>中获取全部的图片，以及描述
        photo = response.xpath('//script[6]/text()').get()
        #img
        img = r', img: (.*?), listimg'
        img_all = re.findall(img,photo)

        item['img'] = ''.join(img_all)
        #img_details
        details =  r'title: (.*?), timg'
        img_details = re.findall(details,photo)

        item['img_details'] = ''.join(img_details)
        
        #url
        item['url'] = response.url

        yield item