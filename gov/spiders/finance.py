import math
import time

import scrapy
import re

from gov.items import GovItem

# 财政数据
class FinanceSpider(scrapy.Spider):
    name = 'finance'
    # 财政部 'http://www.mof.gov.cn/zhengwuxinxi/caizhengshuju/index.htm',
    # 重庆财政局 'http://jcz.cq.gov.cn/html/xxgk/czsj',
    # 北京财政局 'http://www.bjcz.gov.cn/zwxxcs'
    # 深圳财政局 'http://www.szfb.gov.cn/zwgk'
    # 上海财政局 'https://www.czj.sh.gov.cn/was5/web/search?channelid=209150'
    # 广东财政局 'http://czt.gd.gov.cn/zdlyxxgk/index.html'
    # 四川财政局 'http://www.sccz.gov.cn/new_web/new_NewListRight.jsp?id=3&nYear=0&page=0'
    # 浙江财政局 'http://www.zjczt.gov.cn'
    # 天津财局 'http://www.tjcs.gov.cn'
    # 河北财政局 'http://czt.hebei.gov.cn/root17'
    # 山西财政局 'http://www.sxscz.gov.cn/cms_list.action?classId=8a8abd8733290fda013329349a45002c'
    start_urls = [
 'http://www.mof.gov.cn/zhengwuxinxi/caizhengshuju/index.htm' ]

    def parse(self, response):
        channel_url = str(response.url).strip()
        print("--------" + channel_url + "-------------")
        # 财政部 数据统计
        if 'http://www.mof.gov.cn' in channel_url:
            str_body = response.body.decode(response.encoding)
            # 获取总页数
            pattern = re.compile(r'(?<=var countPage = )\d*')
            match = pattern.search(str_body)
            if match:
                for i in range(int(match.group())):
                    if i == 0:
                        page_htm = "index.htm"
                    else:
                        page_htm = "index_" + str(i) + ".htm"
                    yield scrapy.Request(self.create_mof_cn_url(page_htm), callback=self.mof_cn_index_detail)
        # 重庆财政局 数据统计
        if 'http://jcz.cq.gov.cn' in channel_url:
            module_path = '//*[@id="contentx1"]/div/div/dl/dt/a/@href'
            modules = response.xpath(module_path)
            if len(modules) != 0:
                for module in modules:
                    module_url = "http://jcz.cq.gov.cn" + module.extract()
                    yield scrapy.Request(module_url, callback=self.jcz_cq_module_index_parse)
        # 北京财政局 数据统计
        if 'http://www.bjcz.gov.cn' in channel_url:
            module_path = "//div[@class='czsj-sj ']/div/ul/a/@href"
            modules = response.xpath(module_path).extract()
            if len(modules) != 0:
                for module in modules:
                    module_url = "http://www.bjcz.gov.cn" + module
                    yield scrapy.Request(module_url, callback=self.bjcz_module_index_parse)
        # 深圳财政局 重点领域信息公开专栏
        if 'http://www.szfb.gov.cn' in channel_url:
            module_path = "//div[@class='catalog']/ul/li[9]/div[@class='cw-right']/div/a/@href"
            modules = response.xpath(module_path).extract()
            if len(modules) != 0:
                for module in modules:
                    # 移除./ 并拼接url
                    module_url = response.url + module[2:]
                    yield scrapy.Request(module_url, callback=self.szfb_module_index_parse)
        # 上海财政局 财政数据 //div[@class='matter-result']/ul/li
        if 'https://www.czj.sh.gov.cn' in channel_url:
            str_body = response.body.decode(response.encoding)
            # 获取总页数
            pattern = re.compile(r'(?<=var xwnum = )\d*')
            match = pattern.search(str_body)
            if match:
                list_size = int(match.group())
                if list_size > 500:
                    perpage = 60
                elif list_size > 300:
                    perpage = 40
                elif list_size >100:
                    perpage = 20
                else:
                    perpage = 10
                # 向上取整
                page_num = math.ceil(list_size / perpage)
                page = 1
                while page <= page_num:
                    page_url = self.create_sh_page_url(page, perpage, 10) #默认outlinepage为10
                    page = page + 1
                    yield scrapy.Request(page_url, callback=self.sh_index_detail)
        # 广东财政局 重点领域公开（财政数据）
        if 'http://czt.gd.gov.cn' in channel_url:
            modules = response.xpath("//div[@class='hjjs' and not(@id='ggfw')]/h3/a/@href").extract()
            if len(modules) != 0:
                for module in modules:
                    yield scrapy.Request(module, callback=self.gd_index_detail)
        # 四川财政局 财政数据
        if 'http://www.sccz.gov.cn' in channel_url:
            page_info = response.xpath("//td[@class='newstitletext05']/a[4]/@href").extract()[0]
            # 获取总页数
            pattern = re.compile(r'(?<=page=)\d*')
            match = pattern.search(page_info)
            if match:
                for i in range(int(match.group())):
                    page_url = "http://www.sccz.gov.cn/new_web/new_NewListRight.jsp?id=3&nYear=0&page={0}".format(str(i+1))
                    yield scrapy.Request(page_url, callback=self.sc_index_detail)
        # 浙江财政局 重点信息公开
        if 'http://www.zjczt.gov.cn' in channel_url:
            modules = response.xpath("//div[contains(@id,'cz_title')]/div/a/@href").extract()
            if modules:
                for module in modules:
                    yield scrapy.Request(channel_url + module, callback=self.zj_index_detail)
        # 天津财政局 统计数据及公开报告
        if 'http://www.tjcs.gov.cn' in channel_url:
            common_url ="http://www.tjcs.gov.cn/module/jslib/jquery/jpage/dataproxy.jsp?startrecord=1&endrecord=15&perpage=15&col=1&appid=1&webid=1&path=/&columnid={0}" \
                        "&sourceContentType=1&unitid={1}&webname=天津市财政局&permissiontype=0"
            # 统计数据 、 公开报告
            modules = ['17:5940',
                       '27:8965']
            for module in modules:
                list = module.split(':')
                columnid = list[0]
                unitid = list[1]
                page_url = common_url.format(columnid, unitid)
                yield scrapy.Request(page_url, callback=self.tj_index_detail)
        # 河北财政局
        if 'http://czt.hebei.gov.cn' in channel_url:
            # 预决算 统计数据
            ids = ['c_3050', 'c_3053']
            for id in ids:
                module_path = "//*[@id='" + id + "']/@href"
                module = response.xpath(module_path).extract()[0]
                module_url = response.url + module.replace('./', '')
                yield scrapy.Request(module_url, callback=self.hb_pages_detail)
        # 山西财政局
        if 'http://www.sxscz.gov.cn' in channel_url:
            pages_str = str(response.xpath('//*[@id="myForm"]/text()').extract())
            pattern = re.compile(r'(?<=(共))\S*?(?=(行))')
            match = pattern.search(pages_str)
            if match:
                pageSize = int(match.group())
                detail_url = channel_url+ "&pageNo=1&pageSize={0}".format(pageSize)
                yield scrapy.Request(detail_url, callback=self.sx_index_detail)

    def sx_index_detail(self, response):
        items = response.xpath("//div[@class='list_bd news_a']/ul/li[not(@class='line')]")
        if items:
            for item in items:
                title = item.xpath("./p/a/text()").extract()[0].replace('·', '')
                time_str = str(item.xpath("./text()").extract())
                pattern = re.compile(r'(\d{4}-\d{1,2}-\d{1,2})')
                match = pattern.search(time_str)
                pub_time = ''
                if match:
                    pub_time = match.group()
                detail_url = item.xpath("./p/a/@href").extract()[0]
                if '/' == detail_url[0:1]:
                    detail_url = "http://www.sxscz.gov.cn" + detail_url
                else:
                    detail_url = "http://www.sxscz.gov.cn/" + detail_url
                yield scrapy.Request(detail_url,
                                     callback=lambda response, title=title, pub_time=pub_time: self.sx_content_detail(
                                         response, title, pub_time))

    def sx_content_detail(self, response, title, pub_time):
        org_info = "山西财政局"
        content = response.xpath("//div[@class='cont_bc neirong']").extract()[0]
        item = GovItem()
        item['title'] = title
        item['content'] = content
        item['sourceOrg'] = org_info
        item['comments'] = ''
        item['publishTime'] = pub_time
        item['sourceUrl'] = response.url
        yield item
    def hb_pages_detail(self, response):
        regex = re.compile("([^/][^/]+)$")
        m_sPageName = regex.findall(response.url)[0].replace('.htm', '')
        str_body = response.body.decode(response.encoding)
        pattern = re.compile(r'(?<=(m_nRecordCount = "))\S*?(?=("))')
        match = pattern.search(str_body)
        if match:
            list_size = int(match.group())
            m_nPageSize = 15
            m_sPageExt = "htm"
            page_num = math.ceil(list_size / m_nPageSize)
            page = 1
            while page <= page_num:
                if page == 1:
                    sURL = m_sPageName + "." + m_sPageExt;
                else:
                    sURL = m_sPageName + "_" + str((page-1)) + "." + m_sPageExt;
                page_url = re.sub('([^/][^/]+)$', sURL, response.url)
                page = page + 1
                yield scrapy.Request(page_url, callback=self.hb_index_detail)

    def hb_index_detail(self, response):
        items = response.xpath("//tr[@class='lanmucontent_tr']")
        if items:
            for item in items:
                title = item.xpath("./td[1]/a/text()").extract()[0]
                pub_time = item.xpath("./td[4]/text()").extract()[0]
                detail_url = "http://czt.hebei.gov.cn/root17" + item.xpath("./td[1]/a/@href").extract()[0].replace('../', '/')
                yield scrapy.Request(detail_url,
                                     callback=lambda response, title=title, pub_time=pub_time: self.hb_content_detail(
                                         response, title, pub_time))

    def hb_content_detail(self, response, title, pub_time):
        org_info = "河北省财政厅"
        content = response.xpath("//div[@class='content']").extract()[0]
        item = GovItem()
        item['title'] = title
        item['content'] = content
        item['sourceOrg'] = org_info
        item['comments'] = ''
        item['publishTime'] = pub_time
        item['sourceUrl'] = response.url
        yield item

    def tj_index_detail(self, response):
        total_records = response.xpath("//datastore/totalrecord/text()").extract()[0]
        total_url = re.sub(r'(?<=(perpage=))\S*?(?=(&))', total_records, response.url)
        yield scrapy.Request(total_url, callback=self.tj_pages_detail)

    def tj_pages_detail(self, response):
        items = response.xpath("//datastore/recordset/record/text()").extract()
        if items:
            for item in items:
                pattern = re.compile(r'(\d{4}-\d{1,2}-\d{1,2})')
                match = pattern.search(item)
                pub_time = ''
                if match:
                    pub_time = match.group()
                pattern1 = re.compile(r'(?<=(title=\'))\S*?(?=(\'))')
                match1 = pattern1.search(item)
                title = ''
                if match1:
                    title = match1.group()
                pattern2 = re.compile(r'(?<=(href=\'))\S*?(?=(\'))')
                match2 = pattern2.search(item)
                if match2:
                    detail_url = "http://www.tjcs.gov.cn" + match2.group()
                    yield scrapy.Request(detail_url, callback=lambda response, title=title, pub_time=pub_time: self.tj_content_detail(response, title, pub_time))

    def tj_content_detail(self, response, title, pub_time):
        content = response.xpath("//div[@id='zoom']").extract()[0]
        org_info = response.xpath("//table[@id='c']/tr[3]/td/span[2]/text()").extract()[0]
        source_org = org_info.replace('来源：', '')
        item = GovItem()
        item['title'] = title
        item['content'] = content
        item['sourceOrg'] = source_org
        item['comments'] = ''
        item['publishTime'] = pub_time
        item['sourceUrl'] = response.url
        yield item

    def zj_index_detail(self, response):
        str_body = response.body.decode(response.encoding)
        pattern = re.compile(r'(?<=(a href="))\S*(?=(">))')
        match = pattern.search(str_body)
        if match:
            detail_url = "http://www.zjczt.gov.cn" + match.group()
            yield scrapy.Request(detail_url, callback=self.zj_page_detail)

    def zj_page_detail(self, response):
        detail_objs = response.xpath("//recordset/record/text()").extract()
        if len(detail_objs):
            for item in detail_objs:
                pattern = re.compile(r'(?<=(href="))\S*(?=("))')
                match = pattern.search(item)
                if match:
                    detail_url = "http://www.zjczt.gov.cn" + match.group()
                    yield scrapy.Request(detail_url, callback=self.zj_content_detail)

    def zj_content_detail(self, response):
        str_body = response.body.decode(response.encoding)
        # 获取总页数
        pattern1 = re.compile(r'(?<=(发布日期：))\S*?(?=(</td))')
        match_time = pattern1.search(str_body)
        pub_time = ''
        if match_time:
            pub_time = match_time.group()
        pattern2 = re.compile(r'(?<=(信息来源]>begin-->))\S*?(?=(<!))')
        match_org = pattern2.search(str_body)
        org_info = '浙江财政局'
        if match_org:
            org_info = match_org.group()
        content = response.xpath("//div[@id='zoom']").extract()[0]
        title = response.xpath("//title/text()").extract()[0]
        item = GovItem()
        item['title'] = title
        item['content'] = content
        item['sourceOrg'] = org_info
        item['comments'] = ''
        item['publishTime'] = pub_time
        item['sourceUrl'] = response.url
        yield item

    def sc_index_detail(self, response):
        page_modules = response.xpath("//table/tbody/tr")
        if len(page_modules) > 0:
            for page_module in page_modules:
                detail_id_str = page_module.xpath("./td[1]/@onclick").extract()[0]
                pattern = re.compile(r'[0-9]+')
                match = pattern.search(detail_id_str)
                if match:
                    detail_id = match.group()
                    t = time.time()
                    ts = int(round(t * 1000))
                    detail_url = "http://www.sccz.gov.cn/new_web/new_NewShow.jsp?action=1&id={0}&tname=财政数据&TS={1}".format(detail_id, ts)
                    yield scrapy.Request(detail_url, callback=self.sc_content_detail)

    def sc_content_detail(self, response):
        title = response.xpath("//div[@class='infoTxt']/p/text()").extract()[0]
        org_info = response.xpath("//div[@class='infoTxt']/div[1]/div[1]/text()").extract()[0]
        pub_time = response.xpath("//div[@class='infoTxt']/div[1]/div[2]/text()").extract()[0]
        content = response.xpath("//div[@class='txt2-in']").extract()[0]
        source_org = org_info.replace('信息来源：', '')
        if source_org is '':
            source_org = "四川财政局"
        item = GovItem()
        item['title'] = title
        item['content'] = content
        item['sourceOrg'] = source_org
        item['comments'] = ''
        item['publishTime'] = pub_time
        item['sourceUrl'] = response.url
        yield item

    def gd_index_detail(self, response):
        pages_str = response.xpath("//div[@class='pages']/a[@class='last']/@href").extract()[0]
        if ('index.html' in pages_str) or ('index.htm' in pages_str):
            detail_url = response.url
            yield scrapy.Request(detail_url, callback=self.gd_page_detail, dont_filter=True)
        elif 'index_' in pages_str:
            pattern = re.compile(r'[0-9]+')
            match = pattern.search(pages_str)
            if match:
                for i in range(int(match.group())):
                    if i == 0:
                        detail_url = response.url
                    else:
                        content_url = re.sub(r'([/][^/]+)$', "/", response.url)
                        detail_url = content_url + "index_" + str(i + 1) + ".html"
                    yield scrapy.Request(detail_url, callback=self.gd_page_detail, dont_filter=True)

    def gd_page_detail(self, response):
        page_modules = response.xpath("//div[@class='content']/ul/li")
        if len(page_modules) != 0:
            for module in page_modules:
                title = module.xpath("./span/a/text()").extract()[0]
                pub_time = module.xpath("./div[@class='lists_time']/text()").extract()[0]
                detail_url = module.xpath("./span/a/@href").extract()[0]
                if ('html' in detail_url) or ('htm' in detail_url):
                    yield scrapy.Request(detail_url, callback=lambda response, title=title, pub_time=pub_time: self.gd_content_detail(response, title, pub_time))

    def gd_content_detail(self, response, title, pub_time):
        org_info = response.xpath("//div[@class='meta']/div/span[2]/text()").extract()[0]
        source_org = org_info.replace('来源：', '')
        if source_org is '':
            source_org = "广东财政局"
        content = response.xpath("//div[@class='content']/p").extract()[0]
        item = GovItem()
        item['title'] = title
        item['content'] = content
        item['sourceOrg'] = source_org
        item['comments'] = ''
        item['publishTime'] = pub_time
        item['sourceUrl'] = response.url
        yield item

    def create_sh_page_url(self, page, perpage, outlinepage ):
        page_url = "https://www.czj.sh.gov.cn/was5/web/search?page={0}&channelid=209150&perpage={1}&outlinepage={2}"
        return page_url.format(page, perpage, outlinepage)

    def sh_index_detail(self, response):
        page_modules = response.xpath("//div[@class='matter-result']/ul/li")
        if len(page_modules) != 0:
            for module in page_modules:
                pub_time = module.xpath("./span/text()").extract()[0]
                title = module.xpath("./a/text()").extract()[0]
                detail_url = module.xpath("./a/@href").extract()[0]
                if ('.htm' in detail_url) or ('.html' in detail_url) or ('.shtml' in detail_url):
                    if '/' == detail_url[0:1]:
                        detail_url = "https://www.czj.sh.gov.cn" + detail_url
                    yield scrapy.Request(detail_url, callback=lambda response, title=title, pub_time=pub_time: self.sh_content_detail(response, title, pub_time))

    def sh_content_detail(self, response, title, pub_time):
        content = response.xpath("//div[@class='article_content']").extract()[0]
        item = GovItem()
        item['title'] = title
        item['content'] = content
        item['sourceOrg'] = "上海财政局"
        item['comments'] = ''
        item['publishTime'] = pub_time
        item['sourceUrl'] = response.url
        yield item

    def szfb_module_index_parse(self, response):
        count_info = response.xpath("//div[@class='list-content-page']/script/text()").extract()[0]
        count_page = count_info.split(',')[0].replace('createPageHTML(', '')
        for i in range(int(count_page)):
            if i == 0:
                page_htm = ""
            else:
                page_htm = "index_" + str(i) + ".htm"
            page_url = response.url + page_htm
            yield scrapy.Request(page_url, callback=self.szfb_index_detail)

    def szfb_index_detail(self, response):
        page_modules = response.xpath("//div[@class='list-content-list']/ul/li[not(@class='tou')]")
        if len(page_modules) != 0:
            for module in page_modules:
                title = module.xpath("./span[2]/a/text()").extract()[0]
                pub_time = module.xpath("./span[3]/text()").extract()[0]
                detail_url = module.xpath("./span[2]/a/@href").extract()[0]
                if ('.htm' in detail_url) or ('.html' in detail_url):
                    if './' == detail_url[0:2]:
                        content_url = re.sub(r'([/][^/]+)$', "", response.url)
                        detail_url = content_url + detail_url[1:]
                    print(detail_url)
                    yield scrapy.Request(detail_url, callback=lambda response, title=title, pub_time=pub_time: self.szfb_content_detail(response, title, pub_time))

    def szfb_content_detail(self, response, title, pub_time):
        org_info = response.xpath("//div[@class='tit']/h6/span[1]/text()").extract()[0]
        content = response.xpath("//div[@class='news_cont_d_wrap']").extract()[0]
        item = GovItem()
        item['title'] = title
        item['content'] = content
        item['sourceOrg'] = org_info.replace('信息来源：', '')
        item['comments'] = ''
        item['publishTime'] = pub_time
        item['sourceUrl'] = response.url
        yield item

    def bjcz_module_index_parse(self, response):
        str_body = response.body.decode(response.encoding)
        # 获取总页数
        pattern = re.compile(r'(?<=var pageCount = )\d*')
        match = pattern.search(str_body)
        if match:
            for i in range(int(match.group())):
                if i == 0:
                    page_htm = "index.htm"
                else:
                    page_htm = "index_" + str(i) + ".htm"
                page_url = response.url.replace('index.htm', page_htm)
                yield scrapy.Request(page_url, callback=self.bjcz_index_detail)

    def bjcz_index_detail(self, response):
        page_path = '//div[@class="ul-back"]/ul/li'
        page_modules = response.xpath(page_path)
        if len(page_modules) != 0:
            for module in page_modules:
                title = module.xpath('./a/text()').extract()[0]
                detail_url = module.xpath('./a/@href').extract()[0]
                if (('.html' or 'htm') in detail_url) and (('index.html' or 'index.htm') not in detail_url):
                    #拼接url
                    if './' == detail_url[0:2]:
                        content_url = re.sub(r'([/][^/]+)$', "", response.url)
                        detail_url = content_url + detail_url[1:]
                    yield scrapy.Request(detail_url, callback=lambda response, title=title: self.bjcz_content_detail(response, title))

    def bjcz_content_detail(self, response, title):
        pub_time = response.xpath("//span[@style='display: inline-block;margin:15px 10px;font-size: 14px;'][1]/text()").extract()[0]
        content = response.xpath("//div[@class='txt']").extract()[0]
        item = GovItem()
        item['title'] = title
        item['content'] = content
        item['sourceOrg'] = "北京财政局"
        item['comments'] = ''
        item['publishTime'] = pub_time
        item['sourceUrl'] = response.url
        yield item

    #获取各模块 页面总数详情
    def jcz_cq_module_index_parse(self, response):
        count_path = '//*[@id="contentx1"]/div/div[2]/span[4]'
        str_count = response.xpath(count_path).extract()[0]
        pattern = re.compile(r'\d+')
        match = pattern.search(str_count)
        if match:
            for i in range(int(match.group())):
                if i == 0:
                    page_html = ''
                else:
                    page_html = 'List_' + str(i + 1) + '.shtml'
                detail_page_url = response.url + page_html
                yield scrapy.Request(detail_page_url, callback=self.jcz_cq_index_detail)

    #获取每页详情数据
    def jcz_cq_index_detail(self, response):
        page_path = '//*[@id="contentx1"]/div/div/dl/dd/ul/li'
        page_modules = response.xpath(page_path)
        if len(page_modules) != 0:
            for module in page_modules:
                pub_time = module.xpath('./span/text()').extract()[0]
                title = module.xpath('./a/text()').extract()[0]
                content_url = module.xpath('./a/@href').extract()[0]
                if '.shtml' in content_url:
                    if 'jcz.cq.gov.cn' not in content_url:
                        detail_url = 'http://jcz.cq.gov.cn' + content_url
                    else:
                        detail_url = content_url
                yield scrapy.Request(detail_url, callback=lambda response, title=title, pub_time=pub_time: self.jcz_cq_content_detail(response, title, pub_time))

    def jcz_cq_content_detail(self, response, title, pub_time):
        content = response.xpath("//div[@id='showcontent']").extract()[0]
        #org_info = response.xpath("//*[@id='text']/h3/text()").extract()[0]
        item = GovItem()
        item['title'] = title
        item['content'] = content
        item['sourceOrg'] = "重庆财政局"
        item['comments'] = ''
        item['publishTime'] = pub_time
        item['sourceUrl'] = response.url
        yield item

    def mof_cn_parse(self, response):
        str_body = response.body.decode(response.encoding)
        # 获取总页数
        pattern = re.compile(r'(?<=var countPage = )\d*')
        match = pattern.search(str_body)
        if match:
            for i in range(int(match.group())):
                if i == 0:
                    page_htm = "index.htm"
                else:
                    page_htm = "index_" + str(i) + ".htm"
                yield scrapy.Request(self.create_mof_cn_url(page_htm), callback=self.mof_cn_detail)

    def mof_cn_index_detail(self, response):
        modules = response.xpath('//table[@class="ZIT"]/tr/td')
        for module in modules:
            detail_path = "./a/@href"
            detail_url = module.xpath(detail_path).extract()[0]
            # pdf\xls文件直接过滤
            #if ('.pdf' not in detail_url) and ('.xls' not in detail_url):
            if (('.html' or 'htm') in detail_url) and (('index.html' or 'index.htm') not in detail_url):
                # ./开头
                if './' == detail_url[0:2]:
                    detail_url = self.create_mof_cn_url(detail_url[2:])
                if '../' == detail_url[0:3]:
                    detail_url = "http://www.mof.gov.cn/zhengwuxinxi/" + detail_url[3:]
                title_path = "./a/text()"
                title = module.xpath(title_path).extract()[0]
                time_path = "./text()"
                pub_time = module.xpath(time_path).extract()[2].strip().replace('（', '').replace('）', '')
                #print('title: ' + title + '  pub_time: ' + pub_time + '  detail_url: ' + detail_url + '\n')
                yield scrapy.Request(detail_url, callback=lambda response, title=title, pub_time=pub_time: self.mof_cn_content_detail(response, title, pub_time))

    def mof_cn_content_detail(self, response, title, pub_time):
        org_path = '//*[@id="tb_select"]/option/text()'
        source_org = response.xpath(org_path).extract()
        if len(source_org) == 0:
            source_org = '财政部'
        else:
            source_org = source_org[0]
        content_path = '//*[@id="Zoom"]'
        content = response.xpath(content_path).extract()[0]
        item = GovItem()
        item['title'] = title
        item['content'] = content
        item['sourceOrg'] = source_org
        item['comments'] = ''
        item['publishTime'] = pub_time
        item['sourceUrl'] = response.url
        yield item

    def create_mof_cn_url(self, page_htm):
        comment_url = "http://www.mof.gov.cn/zhengwuxinxi/caizhengshuju/{0}"\
            .format(page_htm)
        return comment_url