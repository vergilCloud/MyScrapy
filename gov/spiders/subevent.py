import re
import time
import scrapy
from gov.items import GovItem

class SubeventSpider(scrapy.Spider):
    name = 'subevent'
    start_urls = ['https://www.baidu.com/?tn=news']

    def parse(self, response):
        hot_list = ['http://top.baidu.com/buzz?b=342&c=513&fr=topbuzz_b42_c513',
                    'http://top.baidu.com/buzz?b=341&c=513&fr=topbuzz_b42_c513',
                    'http://top.baidu.com/buzz?b=42&c=513&fr=topbuzz_b342_c513']
        sub_name_list = []
        for line in open("E:\workspace\scrapy-project\gov\\top_sub.txt", "r", encoding="utf-8"):
            # print line,  #python2 用法
            sub_name_list.append(line)
        '''for hot_url in hot_list:
            sourceReq = requests.get(hot_url)
            sourceReq.encoding = 'gb2312'
            sourceHtml = sourceReq.text
            selector = etree.HTML(sourceHtml)
            items = selector.xpath("//table[@class='list-table']/tr")
            count_index = 1
            for item in items:
                if count_index != 1:
                    subject_name = item.xpath("./td[@class='keyword']/a[@class='list-title']/text()")[0]
                    sub_name_list.append(subject_name)
                count_index = count_index + 1'''
        if len(sub_name_list) > 0:
            # 去掉重复主题
            dist_list = list(set(sub_name_list))
            print(len(dist_list))
            for keyword in dist_list:
                keyword = keyword.replace('\n', '').replace('\ufeff', '')
                total = 0
                # 设定爬取页数为10页
                while total < 8:
                    pn = total * 10
                    search_url = self.gen_search_url(keyword, pn)
                    yield scrapy.Request(search_url, callback=lambda response, keyword=keyword: self.bd_req_page(response, keyword))
                    total = total + 1

    def gen_search_url(self, keyword, pn):
            search_url = "https://www.baidu.com/s?ie=utf-8&cl=2&rtt=1&bsst=1&tn=news&word={0}&pn={1}"
            return search_url.format(keyword, pn)

    def bd_req_page(self, response, keyword):
        items = response.xpath("//div[@class='result']")
        for item in items:
            title = item.xpath("./h3/a").xpath('string(.)').extract()[0].replace('\n', '').replace(' ', '')
            source_time = item.xpath("./div/p").xpath('string(.)').extract()[0].replace('\n', '').replace('\t', '') \
                .replace(' ', '').split('\xa0')  # 以空格为分隔符，包含 \n
            source_org = source_time[0]
            whole_time = source_time[2]
            if '小时前' in whole_time:
                # 当前时间毫秒
                t = time.time()
                timeStamp = int(round(t * 1000))
                hoursStamp = int(whole_time.replace('小时前', '')) * 60 * 60 * 1000
                pub_time = timeStamp - hoursStamp
            elif '分钟前' in whole_time:
                t = time.time()
                timeStamp = int(round(t * 1000))
                hoursStamp = int(whole_time.replace('分钟前', '')) * 60 * 1000
                pub_time = timeStamp - hoursStamp
            else:
                # 2018年07月18日10:05
                format_time = whole_time.replace('年', '-').replace('月', '-').replace('日', ' ')
                timeArray = time.strptime(format_time, "%Y-%m-%d %H:%M")
                pub_time = int(time.mktime(timeArray) * 1000)
            source_url = item.xpath("./h3/a/@href").extract()[0]
            if 'baijiahao.baidu.com' in source_url:
                print('baijiahao')
                yield scrapy.Request(source_url, callback=lambda response, title=title, source_org=source_org, pub_time=pub_time, source_url=source_url, keyword=keyword: self.req_bjh_content(response, title, source_org, pub_time, source_url, keyword))
                '''sourceReq = requests.get(source_url)
                sourceReq.encoding = 'utf-8'
                sourceHtml = sourceReq.text
                selector = etree.HTML(sourceHtml)
                content_items = selector.xpath("//div[@class='article-content']/p")
                for content_item in content_items:
                   print(content_item.xpath("./text()"))'''
            else:
                print('not baijiahao')
                str_content = item.xpath("./div").extract()[0].replace('\n', '').replace('\t', '').replace(' ', '')
                pattern1 = re.compile(r'(?<=(</p>))\S*?(?=(<span))')
                match_content = pattern1.search(str_content)
                if match_content:
                    content = match_content.group().replace('<em>', '').replace('</em>', '')
                else:
                    content = item.xpath("./div/text()").extract()[0]
                govItem = GovItem()
                govItem['title'] = title
                govItem['content'] = content
                govItem['sourceOrg'] = source_org
                govItem['comments'] = ''
                govItem['publishTime'] = pub_time
                govItem['sourceUrl'] = source_url
                govItem['subName'] = keyword
                yield govItem

    def req_bjh_content(self, response, title, source_org, pub_time, source_url, keyword):
        contents = response.xpath("//div[@class='article-content']/p").xpath('string(.)').extract()
        print('++++++++++++')
        content = ''
        for item in contents:
            content = content + item + '\n'
        print(content)

        govItem = GovItem()
        govItem['title'] = title
        govItem['content'] = content
        govItem['sourceOrg'] = source_org
        govItem['comments'] = ''
        govItem['publishTime'] = pub_time
        govItem['sourceUrl'] = source_url
        govItem['subName'] = keyword
        yield govItem