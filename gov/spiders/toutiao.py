# -*- coding: utf-8 -*-
import random
import re
import time
import scrapy
import json

from bs4 import BeautifulSoup

from gov.items import GovItem


class Toutiao1Spider(scrapy.Spider):
    name = 'toutiao'
    allowed_domains = ['toutiao.com']
    # 'https://www.toutiao.com/api/pc/feed/?category=news_finance&utm_source=toutiao&widen=1&max_behot_time=0&max_behot_time_tmp=0&tadrequire=true&as=A1C5BCC19B80526&cp=5C1B00C542066E1&_signature=Nxs7FQAAawadNHuVB2mBujcbOw'
    start_urls = ['https://www.toutiao.com/api/pc/feed/?category=news_finance&utm_source=toutiao&widen=1&max_behot_time=0&max_behot_time_tmp=0&tadrequire=true&as=A1C5BCC19B80526&cp=5C1B00C542066E1&_signature=Nxs7FQAAawadNHuVB2mBujcbOw']
    cookies = ['tt_webid=6636900679845856771; Domain=.toutiao.com; expires=Wed, 20-Mar-2099 20:53:57 GMT; Max-Age=7804800; Path=/',
               'tt_webid=6636210639856240136; Domain=.toutiao.com; expires=Wed, 20-Mar-2099 20:53:57 GMT; Max-Age=7804800; Path=/']
    header1 = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
               'Referer': 'https://www.toutiao.com/ch/news_finance/',
               #'cookie': random.choice(cookies),
               'Host': 'www.toutiao.com',
              # 'X-Requested-With': 'XMLHttpRequest',
               ':authority': 'www.toutiao.com'
               }
    header2 = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134',
        'Referer': 'https://www.toutiao.com/ch/news_military/',
        'cookie': 'tt_webid=6643685966840382983; Domain=.toutiao.com; expires=Sun, 07-Apr-2099 17:34:48 GMT; Max-Age=7804800; Path=/',
        'Host': 'www.toutiao.com',
        'X-Requested-With': 'XMLHttpRequest',
        ':authority': 'www.toutiao.com'
        }
    header3 = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Referer': 'https://www.toutiao.com/ch/news_military/',
        'cookie': 'tt_webid=6636948273511073293; Domain=.toutiao.com; expires=Mon, 15-Apr-2019 21:40:54 GMT; Max-Age=7804800; Path=/',
        'Host': 'www.toutiao.com',
        'Connection': 'Keep - Alive',
        'X-Requested-With': 'XMLHttpRequest',
        ':authority': 'www.toutiao.com'
    }

    def parse(self, response):
        channel_url = str(response.url).strip()
        yield scrapy.Request(channel_url, callback=self.request_back, headers=self.header1)

    def request_back(self, response):
        data = json.loads(response.text)
        if ('message' in data.keys()):
            message = data['message']
            if message and message.lower() == 'success':
                max_behot_time = data['next']['max_behot_time']
                data_items = data['data']
                for data_item in data_items:
                    title = data_item['title']
                    item_id = data_item['item_id']
                    sourceOrg = data_item['source']
                    timeStamp = data_item['behot_time']
                    timeArray = time.localtime(timeStamp)
                    behotTime = time.strftime("%Y--%m--%d %H:%M:%S", timeArray)
                    detail_url = "https://www.toutiao.com/group/" + item_id
                    #yield scrapy.Request(detail_url, callback=self.content_request, headers=self.header3)
                    #yield scrapy.Request(detail_url, headers=self.header2,
                                         #callback=lambda response, title=title: self.content_request(response, title))
                    if ('comments_count' in data_item.keys()):
                        comment_counts = data_item['comments_count']
                        print("title:  " + title + "  item_id: " + item_id + "  detail_url: " + detail_url
                            + " comment_counts: " + str(comment_counts))
                        comment_url = self.create_comment_url(item_id, 0, comment_counts)
                        #yield scrapy.Request(detail_url, callback=self.content_request, headers=self.headers)
                        yield scrapy.Request(comment_url, headers=self.header1, callback=lambda response, title=title,detail_url=detail_url,sourceOrg=sourceOrg,behotTime=behotTime: self.comment_request(response, title, detail_url, sourceOrg,behotTime))
                    else:
                        print("title:  " + title + "  item_id: " + item_id + "  detail_url: " + detail_url)
                        item = GovItem()
                        item['title'] = title
                        item['content'] = ''
                        item['sourceOrg'] = sourceOrg
                        item['comments'] = ''
                        item['publishTime'] = behotTime
                        item['sourceUrl'] = detail_url
                        yield item
                rewriteUrl = 'https://www.toutiao.com/api/pc/feed/?category=news_finance&utm_source=toutiao&widen=1&max_behot_time={0}&max_behot_time_tmp={0}&tadrequire=true'
                rewriteUrl = rewriteUrl.format(max_behot_time)
                print(rewriteUrl)
                yield scrapy.Request(rewriteUrl, callback=self.request_back, headers=self.header1, dont_filter=True)
            else:
                print(message + "  " + str(response.url).strip())
                time.sleep(2)
                yield scrapy.Request(str(response.url).strip(), callback=self.request_back, headers=self.header1, dont_filter=True)


    def comment_request(self, response, title, detail_url, sourceOrg, behotTime):
        comment_datas = json.loads(response.text)['data']['comments']
        item = GovItem()
        item['title'] = title
        item['content'] = ''
        item['sourceOrg'] = sourceOrg
        item['publishTime'] = behotTime
        item['sourceUrl'] = detail_url
        # 默认大小5
        comments_list = []
        for comment in comment_datas:
            comments_list.append(comment['text'])
        item['comments'] = comments_list
        yield item

    def create_comment_url(self, item_id, offset, count):
        comment_url = "https://www.toutiao.com/api/comment/list/?group_id={0}&item_id={0}&offset={1}&count={2}"\
            .format(item_id, offset, count)
        return comment_url

    def content_request(self, response, title):
        str_body = response.body.decode(response.encoding)
        print(str_body)
        content = self.parse_page_detail(str_body)
        if content is None:
            content = title
        #print(content)
        item = GovItem()
        item['title'] = title
        item['content'] = content
        item['sourceOrg'] = '头条'
        item['publishTime'] = ''
        item['sourceUrl'] = response.url
        item['comments'] = ''
        print(item['content'])
        #yield item

        #json_content = response.xpath("/html/body/script[4]/text()").extract()[0]
        #json_body_str = json_content.replace('articleInfo: {', '').strip()[:-1]
        #json_body = json_body_str.replace('repin: 0,', 'repin: 0')
        #json_str = self.quote_keys_for_json(json_body).replace("''", '"t"')
        #print(json_body_str)

    def parse_page_detail(self, html):
        soup = BeautifulSoup(html, 'lxml')
        pattern = "var BASE_DATA"
        script = soup.find_all('script')
        try:
            for n in script:
                n = n.get_text()
                if 'BASE_DATA' in n:
                    # 使用json将其转换为dict
                    n = n.split("content: '")
                    n = n[1].split('groupId:')
                    info = n[0]
                    print("info   " + info)
                    if info:
                        return info
        except:
            return ""

    def quote_keys_for_json(self, json_str):
        """给键值不带双引号的json字符串的所有键值加上双引号。
        注：解析一般的不严格的json串，可以checkout https://github.com/dmeranda/demjson, 速度比标准库要慢。"""
        quote_pat = re.compile(r'".*?"')
        a = quote_pat.findall(json_str)
        json_str = quote_pat.sub('@', json_str)
        key_pat = re.compile(r'(\w+):')
        json_str = key_pat.sub(r'"\1":', json_str)
        assert json_str.count('@') == len(a)
        count = -1

        def put_back_values(match):
            nonlocal count
            count += 1
            return a[count]

        json_str = re.sub('@', put_back_values, json_str)
        return json_str




