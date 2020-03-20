import collections

import scrapy
import requests
from lxml import etree

from gov.items import GovItem

class TopsubSpider(scrapy.Spider):
    name = 'topsub'
    allowed_domains = ['top.baidu.com']
    # 民生热点
    start_urls = ['http://top.baidu.com/']

    def parse(self, response):
        hot_list = ['http://top.baidu.com/buzz?b=342&c=513&fr=topbuzz_b42_c513',
                   'http://top.baidu.com/buzz?b=341&c=513&fr=topbuzz_b42_c513',
                   'http://top.baidu.com/buzz?b=42&c=513&fr=topbuzz_b342_c513']
        sub_name_list = []
        for hot_url in hot_list:
            sourceReq = requests.get(hot_url)
            sourceReq.encoding = 'gb2312'
            sourceHtml = sourceReq.text
            selector = etree.HTML(sourceHtml)
            items = selector.xpath("//table[@class='list-table']/tr")
            if 'b=342' in hot_url:
                hot_type = '民生热点'
            elif 'b=341' in hot_url:
                hot_type = '今日热点'
            else:
                hot_type = '七日热点'
            count_index = 1
            for item in items:
                if count_index != 1:
                    subject_name = item.xpath("./td[@class='keyword']/a[@class='list-title']/text()")[0]
                    hot_num = item.xpath("./td[@class='last']/span/text()")[0]
                    icon_statu = item.xpath("./td[@class='keyword']/span/@class")
                    status = ''
                    if icon_statu:
                        if 'icon-new' in icon_statu[0]:
                            status = '新'
                            print(status)
                    govItem = GovItem()
                    govItem['subName'] = subject_name
                    govItem['hotNum'] = hot_num
                    govItem['hotType'] = hot_type
                    govItem['status'] = status
                    sub_name_list.append(govItem)
                count_index = count_index + 1
        if len(sub_name_list) > 0:
            dist_list = []
            # 去掉重复主题
            unique = collections.OrderedDict()
            for govItem in sub_name_list:
                unique.setdefault(govItem["subName"], govItem)
            for item in unique.values():
                dist_list.append(item)
                yield item
            print(len(dist_list))

    def req_news_item(self, response):
        print('test')

    def gen_search_url(self, keyword):
            search_url = "http://news.baidu.com/ns?word={0}&pn=0&cl=2&ct=0&tn=news&rn=20&ie=utf-8&bt=0&et=0"
            return search_url.format(keyword)



