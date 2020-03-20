# -*- coding: utf-8 -*-
import datetime
import time

import jsonpath
import scrapy
import json
import requests
import math

from gov.items import GovItem

# 抓取本年度
class WangyiSpider(scrapy.Spider):
    name = 'wangyi'
    allowed_domains = ['163.com']
    # 政解专栏 政策解读 政务要闻 学习之声  地方建设 经济发展 辉煌历程 文化中国 凯风时评 央企动态
    start_urls = [

                'http://gov.163.com/special/zhengjiezhuanti_n',
                  #'http://gov.163.com/special/zwzx_n',
                  #'http://gov.163.com/special/dffg_n',
                  #'http://gov.163.com/special/gcdt_n_14',
                  #'http://gov.163.com/special/zwlz_n/',
                  #'http://gov.163.com/special/jjjs_n/',
                  #'http://gov.163.com/special/hhlc_n/',
                  #'http://gov.163.com/special/cityandfestival_n/',
                  #'http://gov.163.com/special/sdyd_n/',
                  #'http://gov.163.com/special/yangqi_n/'
       ]

    def parse(self, response):
        channel_url = str(response.url).strip()
        if 'zhengjiezhuanti_n' in channel_url:
            yield scrapy.Request(channel_url, callback=self.zhengjiezhuanti_n_parse)
        elif 'dy.163.com/v2/article' in channel_url:
            yield scrapy.Request(channel_url, callback=self.dy_detail_parse)
        else:
            yield scrapy.Request(channel_url, callback=self.common_parse)



    def zhengjiezhuanti_n_parse(self, response):
        avali_types = ['网易政务', '网易', '网易有思']
        module_path = "//ul[@class='newsList']/li"
        modules = response.xpath(module_path)
        for module in modules:
            news_path = "./div[@class='titleBar clearfix']/h3/a/@href"
            detail_url = module.xpath(news_path).extract()[0]
            source_path = "./div[@class='newsBottom clearfix']/p[@class='sourceDate']/span/text()"
            source_type = module.xpath(source_path).extract()
            if source_type and source_type[0] in avali_types:
                # dy 网址的网易有思类型
                dy_pre_url = "http://dy.163.com/v2/article"
                if detail_url.find(dy_pre_url) >= 0:
                    yield scrapy.Request(detail_url, callback=self.dy_detail_parse)
                else:
                    yield scrapy.Request(detail_url, callback=self.detail_parse)

    def dffg_n_parse(self, response):
        page_path = "//div[@class='bar_pages']/a[not(@class='bar_pages_flip')]/@href"
        modules = response.xpath(page_path)
        for module in modules:
            detail_url = module.extract()
            print('\n' + '--------' + detail_url + '--------')
            yield scrapy.Request(detail_url, callback=self.handle_common_request)

    def zwlz_n_parse(self, response):
        page_path = "//div[@class='bar_pages']/a[not(@class='bar_pages_flip')]/@href"
        modules = response.xpath(page_path)
        for module in modules:
            detail_url = module.extract()
            yield scrapy.Request(detail_url, callback=self.handle_common_request)

    def gcdt_n_14_parse(self, response):
        page_path = "//div[@class='bar_pages']/a[not(@class='bar_pages_flip')]/@href"
        modules = response.xpath(page_path)
        for module in modules:
            detail_url = module.extract()
            yield scrapy.Request(detail_url, callback=self.handle_common_request)

    def zwzx_n_parse(self, response):
        page_path = "//div[@class='bar_pages']/a[not(@class='bar_pages_flip')]/@href"
        modules = response.xpath(page_path)
        for module in modules:
            detail_url = module.extract()
            yield scrapy.Request(detail_url, callback=self.handle_common_request)

    def common_parse(self, response):
        page_path = "//div[@class='bar_pages']/a[not(@class='bar_pages_flip')]/@href"
        modules = response.xpath(page_path)
        for module in modules:
            detail_url = module.extract()
            yield scrapy.Request(detail_url, callback=self.handle_common_request)

    def handle_common_request(self, response):
        channel_url = str(response.url).strip()
        print(channel_url)
        title_path = "//div[@class='cnt']/ul/li/a/@href"
        modules = response.xpath(title_path)
        for module in modules:
            detail_url = module.extract()
            yield scrapy.Request(detail_url, callback=self.detail_parse)

    def dy_detail_parse(self, response):
        channel_url = str(response.url).strip()
        detail_module = "//div[@class='article_wrap fl']"
        for module in response.xpath(detail_module):
            title = module.xpath("./div[@class='article_title']/h2/text()").extract()[0].strip()
            pub_path_module = module.xpath("./div[@class='article_title']/div[@class='share_box']")
            publish_time = pub_path_module.xpath("./p/span[1]/text()").extract()[0]
            source_org = pub_path_module.xpath("./p/span[3]/text()").extract()[0]
            comment_url = pub_path_module.xpath("./span/span/a/@href").extract()[0]
            content = module.xpath("./div/div[@class='content']").xpath('string(.)').extract()[0]
            print(content)
            if comment_url:
                # http://comment.tie.163.com/E2O8PQFE054156AE.html
                thread_id = comment_url.split('/')[3].split('.')[0]
                #return self.item_parse(publish_time, title, content, channel_url, thread_id, source_org)

    def create_comment_url(self, thread_id, limit, offset):
        product_id = "a2869674571f77b5a0867c3d71db5856"
        comment_url = "http://comment.api.163.com/api/v1/products/{0}/threads/{1}/comments/newList?" \
                      "ibc=newspc&limit={2}&showLevelThreshold=72&headLimit=1&tailLimit=2&offset={3}"\
            .format(product_id, thread_id, limit, offset)
        return comment_url

    def comment_parse(self, comment_url):
        res = requests.get(comment_url).content
        data = json.loads(res.decode())
        return data

    def detail_parse(self, response):
        channel_url = str(response.url).strip()
        detail_module = "//div[@class='post_content_main']"
        for module in response.xpath(detail_module):
            title = module.xpath("./h1/text()").extract()[0].strip()
            publish_time = module.xpath("./div[@class='post_time_source']/text()").extract()[0]\
                .replace('来源:', '').strip()
            data_year = datetime.datetime.now().year
            content = module.xpath("./div[@class='post_body']/div[@class='post_text']").xpath('string(.)').extract()[0]
            if '2018' not in publish_time:
                return
            source_org = module.xpath("./div[@class='post_time_source']/a[1]/text()").extract()[0].strip()
            thread_id = str(response.url).strip().split('/')[6].split('.')[0]
            return self.item_parse(publish_time, title, content, channel_url, thread_id, source_org)

    def item_parse(self, publish_time, title, content, comment_url, thread_id, source_org):
        detail_comment_url = self.create_comment_url(thread_id, 30, 0)
        item = GovItem()
        item['title'] = title
        item['content'] = content
        item['sourceOrg'] = source_org
        item['publishTime'] = publish_time
        item['sourceUrl'] = comment_url
        print("title: " + title + "  publish_time:  " + publish_time + "   source_org: " + source_org
              + " comment_url: " + comment_url + "publishTime " + publish_time + "content  " +content)
        # 第一次获取总数
        data = self.comment_parse(detail_comment_url)
        list_size = data.get('newListSize')
        if list_size != 0:
            if list_size <= 300:
                limit = 30
            else:
                limit = 40  #只能最大40 不然会报分页参数错误
            page_num = math.ceil(list_size / limit)
            comments_list = []
            page = 0
            while page < page_num:
                offset = page * limit
                detail_comment_url = self.create_comment_url(thread_id, limit, offset)
                print(detail_comment_url)
                data = self.comment_parse(detail_comment_url)
                for key in data['comments'].keys():
                    user_name = jsonpath.jsonpath(data['comments'][key], '$..nickname')
                    if user_name != False:
                        user_name = user_name[0]
                    else:
                        user_name =''
                    location = jsonpath.jsonpath(data['comments'][key], '$..location')
                    if location != False:
                        location = location[0]
                    else:
                        location =''
                    timeArray = time.strptime(data['comments'][key]['createTime'].strip(), "%Y-%m-%d %H:%M:%S")
                    timeStamp = int(time.mktime(timeArray) * 1000)
                    json_str = {
                        "content": data['comments'][key]['content'].replace('[', '').replace(']', ''),
                        "userName": user_name,
                        "place": location,
                        "hotNum": data['comments'][key]['vote'],
                        "publishDate": timeStamp
                    }
                    comments_list.append(json_str)
                page = page + 1
            item['comments'] = comments_list
        else:
            item['comments'] = ''
        yield item