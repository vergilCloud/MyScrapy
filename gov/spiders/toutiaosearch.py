import json

import scrapy


class ToutiaoSpider(scrapy.Spider):
    name = 'toutiaosearch'
    allowed_domains = ['toutiao.com']
    start_urls = [
        'https://www.toutiao.com/api/search/content/?aid=24&offset=0&format=json&keyword=PPP&autoload=true&count=20&cur_tab=1&from=search_tab&pd=synthesis']

    def parse(self, response):
        channel_url = str(response.url).strip()
        data = json.loads(response.text)
        if ('message' in data.keys()):
            message = data['message']
            if message and message.lower() == 'success':
                data_items = data['data']
                for data_item in data_items:
                    if ('title' in data_item.keys()):
                        title = data_item['title']
                        print(title)

    def generate_url(self, offset, count):
        common_url = 'https://www.toutiao.com/api/search/content/?aid=24&offset={0}&format=json&keyword=PPP&autoload=true&count={1}&cur_tab=1&from=search_tab&pd=synthesis'
        return common_url.format(offset, count)