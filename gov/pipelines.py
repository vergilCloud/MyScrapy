# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import random
import time
import requests
from bs4 import BeautifulSoup

class GovPipeline(object):
    headers = {'A-APPID': 'sentiment-gather',
               'A-TIMESTAMP': '3333333333333333',
               'Content-Type': 'application/json'}
    def process_item(self, item, spider):
        if 'topsub' == spider.name:
            self.sub_data_store(item)
        elif 'subevent' == spider.name:
            self.sub_content_data_store(item)
        else:
            soup = BeautifulSoup(item['content'])
            item['content'] = soup.text
        #for s in soup(['script', 'style']):
            #s.decompose()
        #clean_content = ' '.join(soup.stripped_strings)

            if 'wangyi' == spider.name:
                print(item)
                self.data_store(item)
            if 'toutiao' == spider.name:
                file_name = "../data/toutiao/" + "toutiao" + item['sourceUrl'].split('/')[2] + "-" + item['title'] + ".txt"
                self.write_content_file(file_name, item)
            if 'finance' == spider.name:
                print('finance')
            if 'pppsearch' == spider.name:
                print(item['publishTime'] + '\n' + item['title'])
                self.data_store(item)

    def sub_data_store(self, item):
        if len(item['subName'].strip()) != 0 and len(item['hotNum'].strip()) != 0:
            url = 'http://103.28.215.253:10465/app-gateway/sentiment-gather/spider-data/hot-subject/store'
            t = time.time()
            timeStamp = int(round(t * 1000))
            item['sourceOrg'] = '百度'
            subjectDatas = []
            json_str = {
                "hotType": item['hotType'],
                "mediaSource": '百度',
                "mediaType": 'news',
                "name": item['subName'],
                "publishDate": timeStamp,
                'status': item['status'],
                "searchNum": int(item['hotNum'])
            }
            subjectDatas.append(json_str)
            r = requests.post(url, data=json.dumps({'subjectDatas': subjectDatas}), headers=self.headers)
            print(r)
            # 保存到文件
            with open('top_sub.txt', "a", encoding='utf-8') as fp:
                fp.write(item['subName'] + '\n')

    def sub_content_data_store(self, item):
        print(item)
        url = 'http://103.28.215.253:10465/app-gateway/sentiment-gather/spider-data/info/store'
        type = random.randint(1, 3)
        if type == 1:
            media_type = 'news'
        elif type == 2:
            media_type = 'weibo'
        else:
            media_type = 'weixin'
        r = requests.post(url, data=json.dumps({'subjectName': item['subName'],
                                                'title': item['title'].strip().replace('|', '-'),
                                                'publishDate': item['publishTime'],
                                                'mediaSource': item['sourceOrg'].replace('|', '-'),
                                                'mediaType': media_type,
                                                'realtimeType': 'custom_sub',
                                                'url': item['sourceUrl'].replace('|', '-'),
                                                'content': item['content'].strip().replace('|', '-'),
                                                'comments': item['comments']}), headers=self.headers)
        print(r)


    def data_store(self, item):
        if len(item['title'].strip()) !=0 and len(item['content'].strip()) != 0:
            headers = {'A-APPID': 'sentiment-gather',
                       'A-TIMESTAMP': '3333333333333333',
                       'Content-Type': 'application/json'}
            url = 'http://103.28.215.253:10465/app-gateway/sentiment-gather/spider-data/info/store'
            if ':' in item['publishTime'].strip():
                timeArray = time.strptime(item['publishTime'].strip(), "%Y-%m-%d %H:%M:%S")
            else:
                timeArray = time.strptime(item['publishTime'].strip(), "%Y-%m-%d")
            timeStamp = int(time.mktime(timeArray)*1000)
            #print(item['comments'])
            if item['sourceOrg'] == '':
                item['sourceOrg'] = '网易'
            print(item['sourceOrg'])
            type = random.randint(1, 3)
            media_type = ''
            if type == 1:
                media_type = 'news'
            elif type == 2:
                media_type = 'weibo'
            else:
                media_type = 'weixin'
            r = requests.post(url, data=json.dumps({'subjectName': 'PPP模式',
                                                    'title': item['title'].strip().replace('|', '-'),
                                                    'publishDate': timeStamp,
                                                    'mediaSource': item['sourceOrg'].strip().replace('|', '-'),
                                                    'mediaType': media_type,
                                                    'realtimeType': 'custom_sub',
                                                    'url': item['sourceUrl'],
                                                    'content': item['content'].strip().replace('|', '-'),
                                                    'comments': item['comments']}), headers=headers)
            print(r)

    def finance_write_file(self, file_name, item):
        with open(file_name, "a", encoding='utf-8') as fp:
            fp.write(item['title'] + '\n' + item['publishTime'] + '\n' + item['sourceOrg'] + '\n' + item['content'] + '\n')
            if len(item['comments']) != 0:
                fp.write('--------comments------------' + '\n')
                for comment in item['comments']:
                    fp.write(comment + '\n')

    def write_file(self, file_name, item):
        with open(file_name, "a", encoding='utf-8') as fp:
            fp.write('\n' + '--------headers------------' + '\n')
            comments = len(item['comments'])
            str_title = self.seg_sentence(item['title'])
            # 引入TextRank关键词抽取接口
            str_words = self.get_keywords(item['title'])
            fp.write(item['title'] + '\n' + item['publishTime'] + '\n' + item['sourceOrg']+ '\n' + str(comments) + '\n' + item['content'] + '\n' + 'jieba ' + str_title + '\n' + 'keywords ' + str_words + '\n')
            fp.write('--------comments------------' + '\n')
            for comment in item['comments']:
                fp.write(comment + '\n')

    def write_content_file(self, file_name, item):
        if item['title'] and item['content']:
            with open(file_name, "a", encoding='utf-8') as fp:
                fp.write(item['title'] + '\n' + item['content'] + '\n')


    stopwords = ''
    # 创建停用词list
    def stopwordslist(self, filepath):
        stopwords = [line.strip() for line in open(filepath, 'r', encoding='utf-8').readlines()]
        return stopwords

    '''# 关键词提取
     def get_keywords(self, wordstr):
        # 引入TextRank关键词抽取接口
        textrank = analyse.textrank
        keywords = textrank(wordstr)
        # 输出抽取出的关键词
        key_var = ''
        for keyword in keywords:
            key_var += keyword
            key_var += "|"
        return key_var

    # 对标题进行分词
    def seg_sentence(self, sentence):
        sentence_seged = jieba.cut(sentence.strip(), cut_all=False)
        # 这里加载停用词的路径
        stopwords = self.stopwordslist('stopwords.txt')
        outstr = ''
        for word in sentence_seged:
            if word not in stopwords:
                if word != '\t':
                    outstr += word
                    outstr += "|"
        return outstr'''
