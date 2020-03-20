from scrapy.cmdline import execute  # 调用此函数可以执行scrapy的脚本
import sys
import os
import time

# 用来设置工程目录，有了它才可以让命令行生效
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 调用execute()函数执行scarpy的命令 scary crawl 爬虫文件名字
i = 0
while i < 50:
    i = i + 1
    execute(['scarpy', 'crawl', 'toutiao'])
    time.sleep(20)