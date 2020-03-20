import datetime
import json
import re

import scrapy

from gov.items import GovItem


class PPPSpider(scrapy.Spider):
    name = 'pppsearch'
    start_urls = [
        # 新闻动态
        #'http://www.cpppc.org/zh/pppxwdt/index.jhtml',
        # 行业动态
        #'http://www.cpppc.org/zh/ppphyfz/index.jhtml',
        # 招商
        #'http://www.cpppc.org/zh/pppzsfb/index.jhtml',
        # 示范推广
        #'http://www.cpppc.org/zh/pppsftg/index.jhtml',
        # zhiborui 新闻
        #'http://www.zhiborui.com/xwdt',
        # case
        #'http://www.zhiborui.com/case'
        # baidu
        'http://news.baidu.com/ns?word=ppp&pn=0&cl=2&ct=0&tn=news&rn=20&ie=utf-8&bt=0&et=0'
      ]

    def parse(self, response):
        channel_url = str(response.url).strip()
        # 财政部
        if 'http://www.cpppc.org' in channel_url:
            if 'pppsftg' in channel_url:
                modules = response.xpath("//div[@class='dis']/ul[@class='tab']/li/a/@href").extract()
            else:
                modules = response.xpath("//div[@class='tit tit1']/span[@class='more']/a/@href").extract()
            for module in modules:
                yield scrapy.Request(module, callback=self.cpppc_req_module)
        elif 'http://www.zhiborui.com' in channel_url:
            if 'xwdt' in channel_url:
                page_text = response.xpath('//*[@id="pagination"]/center/text()').extract()[0]
                pattern = re.compile(r'(?<=(/))\d*')
                match = pattern.search(page_text)
                if match:
                    page_size = int(match.group())
                    page = 1
                    while page <= page_size:
                        if page == 1:
                            page_url = response.url + 'index.html'
                        else:
                            page_url = response.url + 'index_'+str(page)+'.html'
                        page = page + 1
                        yield scrapy.Request(page_url, callback=self.zbr_req_page, dont_filter=True)
            elif 'case' in channel_url:
                modules = response.xpath("//ul[@id='listnav']/li/a/@href").extract()
                for module in modules:
                    module_url = response.url + module.replace('/case/', '')
                    yield scrapy.Request(module_url, callback=self.zbr_req_module)

        elif 'http://news.baidu.com' in channel_url:
            total = 1
            while total <= 1:
                search_url = 'http://news.baidu.com/ns?word=ppp&pn={0}&cl=2&ct=0&tn=news&rn=20&ie=utf-8&bt=0&et=0'.format(total * 20)
                total = total + 1
                yield scrapy.Request(search_url, callback=self.bd_req_page)

    def bd_req_page(self, response):
        items = response.xpath("//div[@class='result']")
        for item in items:
            #detail_url = item.xpath("./div/span/a/@href").extract()[0]
            title = item.xpath("./h3/a/text()").extract()[0].replace(' ', '').replace('\\n', '')
            '''source_time = item.xpath("./div/p/text()").extract()[0].split( )# 以空格为分隔符，包含 \n
            if len(source_time) == 3:
                source_org = source_time[0]
                pub_time = source_time[1]+source_time[2]
            elif len(source_time) ==2:
                source_org = source_time[0]
                pub_time = source_time[1]
            else:
                source_org = source_time[0]
                pub_time = str(datetime.date.today())
            if pub_time:
               if  '前' in pub_time:
                   pub_time = str(datetime.date.today())
            print (source_org +'\n' +pub_time)'''

            #pub_time = source_time[1]
            content = item.xpath("./div").extract()
            pattern1 = re.compile(r'(?<=(</p>))\S*?(?=(<spanclass))')
            match_content = pattern1.search(str(content).replace(' ', ''))
            whole_content = ''
            if match_content:
                whole_content = match_content.group()
            '''len_content = len(content)
            i = 0
            whole_content = ''
            while i <len_content:
                whole_content = whole_content + content[i]
                i = i +1'''
            whole_content = whole_content.replace('<em>', '').replace('</em>','').replace('\\n', '')
            item = GovItem()
            item['title'] = title
            item['content'] = whole_content
            item['sourceOrg'] = 'baidu'
            item['comments'] = ''
            item['publishTime'] = str(datetime.date.today())
            item['sourceUrl'] = 'www.baidu.com/news/search'
            yield item
            #print(content + "\n" + title + '\n' + pub_time + '\n' + source_org)

            #if title and detail_url and pub_time:
                #yield scrapy.Request(detail_url,
                                 #callback=lambda response, title=title, pub_time=pub_time, source_org = source_org: self.bd_req_content(
                                      #response, title, pub_time, source_org))
    def bd_req_content(self, response, title, pub_time, source_org):
        print(response.url + "\n" + title + '\n' + pub_time + '\n' + source_org)

    def zbr_req_module(self, response):
        page_text = response.xpath('//center').extract()[0]
        pattern = re.compile(r'(?<=(/))\d*')
        match = pattern.search(page_text)
        if match:
            page_size = int(match.group())
            page = 1
            while page <= page_size:
                if page == 1:
                    page_url = response.url + 'index.html'
                else:
                    page_url = response.url + 'index_' + str(page) + '.html'
                page = page + 1
                yield scrapy.Request(page_url, callback=self.zbr_req_page, dont_filter=True)

    def zbr_req_page(self, response):
        if 'xwdt' in response.url:
            items = response.xpath("//div[@class='content']/ul/li")
            for item in items:
                title = item.xpath("./p/a/text()").extract()[0]
                detail_url = item.xpath("./p/a/@href").extract()[0].replace('/xwdt/','')
                content_url = re.sub(r'([/][^/]+)$', "/", response.url)
                detail_url = content_url + detail_url
                yield scrapy.Request(detail_url,
                                    callback=lambda response, title=title: self.zbr_req_content(
                                        response, title))
        elif 'case' in response.url:
            detail_url = 'http://www.zhiborui.com' + response.xpath("//div[@class='list_list_t']/a/@href").extract()[0]
            title = response.xpath("//div[@class='list_list_t']/a/text()").extract()[0]
            yield scrapy.Request(detail_url,
                                 callback=lambda response, title=title: self.zbr_req_content(
                                     response, title))


    def zbr_req_content(self, response, title):
        pub_time = response.xpath("//div[@class='project_d_t']/span/text()").extract()[0]
        content = response.xpath("//div[@class='project_d_c']").extract()[0]
        item = GovItem()
        item['title'] = title
        item['content'] = content
        item['sourceOrg'] = '智博睿'
        item['comments'] = ''
        item['publishTime'] = pub_time
        item['sourceUrl'] = response.url
        yield item

    def cpppc_req_module(self, response):
        page_text = response.xpath("//div[@class='pagesize']/div/text()").extract()[0]
        pattern = re.compile(r'(?<=(/))\d*')
        match = pattern.search(page_text)
        if match:
            page_size = int(match.group())
            page = 1
            while page <= page_size:
                if page == 1:
                    page_url = response.url
                else:
                    content_url = re.sub(r'([/][^/]+)$', "/", response.url)
                    page_url = content_url + 'index_' + str(page) + '.jhtml'
                page = page + 1
                yield scrapy.Request(page_url, callback=self.cpppc_req_page, dont_filter=True)

    def cpppc_req_page(self, response):
        items = response.xpath("//div[@class='conts']/ul/li")
        for item in items:
            pub_time = item.xpath("./em/text()").extract()[0]
            title = item.xpath("./a/@title").extract()[0]
            detail_url = item.xpath("./a/@href").extract()[0]
            yield scrapy.Request(detail_url,
                                 callback=lambda response, title=title, pub_time=pub_time: self.cpppc_req_content(
                                     response, title, pub_time))

    def cpppc_req_content(self, response, title, pub_time):
        content = response.xpath("//div[@class='cont']").extract()[0]
        item = GovItem()
        item['title'] = title
        item['content'] = content
        item['sourceOrg'] = '政府和社会资本合作中心'
        item['comments'] = ''
        item['publishTime'] = pub_time
        item['sourceUrl'] = response.url
        yield item