# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GovItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    content = scrapy.Field()
    sourceOrg = scrapy.Field()
    comments = scrapy.Field()
    publishTime = scrapy.Field()
    sourceUrl = scrapy.Field()
    subName = scrapy.Field()
    hotNum = scrapy.Field()
    hotType = scrapy.Field()
    status = scrapy.Field()
    pass
