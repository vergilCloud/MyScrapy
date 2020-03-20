import scrapy

class WeixinsogoSpider(scrapy.Spider):
    name = 'weixinsogo'
    allowed_domains = ['weixin.sogou.com']
    start_urls = ['https://weixin.sogou.com']

    def parse(self, response):
        channel_url = str(response.url).strip()
        print(channel_url)