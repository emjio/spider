# -*- coding:utf-8 -*-
import gevent
from gevent import monkey
monkey.patch_all(thread=False)
from requests import get
from filetype import guess
from os import rename
from os import makedirs
from os.path import exists
from json import loads
from contextlib import closing
from lxml import etree
from threading import Thread
import redis   # 导入redis 模块
import json
pool = redis.ConnectionPool(host='47.106.128.129', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)
import re
import time
import random
import json

downloadedPIC = 0
dir_NUM = 0
# 文件下载器
def Down_load(file_url, file_full_name, now_photo_count, all_photo_count):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36","Referer":"https://www.mzitu.com/"}

    # 开始下载图片
    with closing(get(file_url, headers=headers, stream=True)) as response:
        chunk_size = 1024  # 单次请求最大值
        content_size = int(response.headers['content-length'])  # 文件总大小
        data_count = 0 # 当前已传输的大小
        with open(file_full_name, "wb") as file:
            for data in response.iter_content(chunk_size=chunk_size):
                file.write(data)
                done_block = int((data_count / content_size) * 50)
                data_count = data_count + len(data)
                now_jd = (data_count / content_size) * 100
                print("\r %s：[%s%s] %d%% %d/%d" % (file_full_name, done_block * '█', ' ' * (50 - 1 - done_block), now_jd, now_photo_count, all_photo_count), end=" ")

    # 下载完图片后获取图片扩展名，并为其增加扩展名
    # file_type = guess(file_full_name)
    rename(file_full_name, file_full_name)

#
def crawler_link(url,num):
    # 获取图片列表数据
    global dir_NUM
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36","Referer":"https://www.mzitu.com/"}
    respond = get(url, headers=headers)
    # time.sleep(random.randint(5,30))
    html = etree.HTML(respond.text)
    photo_data = html.xpath('//ul[@id="pins"]/li/a[1]')
    # pr

    # 已经下载的图片张数
    nextLink= ''
    if len(html.xpath('//a[@class="next page-numbers"]'))>0 :
        nextLink = html.xpath('//a[@class="next page-numbers"]/attribute::href')[0]
    # 开始下载并保存5K分辨率壁纸
    for photo in photo_data:
        dir = photo.xpath('img/attribute::alt')[0]
        dir =  re.compile('[!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\s]+').sub('',dir)
        link = photo.xpath('attribute::href')[0]
        r.lpush(redis_key,json.dumps({"dir":dir,"link":link}))
        # # 创建一个文件夹存放我们下载的图片
        if not exists('./pic/' + str(dir)):
            makedirs('./pic/' + str(dir))
            dir_NUM += 1
    if  False :
        crawler_link(nextLink,wall_paper_count)
    else:
        print('\n目录创建完成!,共发现图集'+str(dir_NUM)+'\n开始图片采集队列')
        loop_picture()
def loop_picture():
    while len(r.lrange(redis_key, 0, 0))>0:
        result = json.loads(r.lrange(redis_key, 0, 0)[0])
        url = result['link']
        dir = result['dir']
        crawler_photo(url,dir)
        r.lpop(redis_key) 

    
# 爬取不同类型图片
def crawler_photo(url,dir):
    global downloadedPIC
    # 获取图片列表数据
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36","Referer":"https://www.mzitu.com/"}
    respond = get(url, headers=headers)
    html = etree.HTML(respond.text)
    file_url = html.xpath('//img[@class="blur"]/attribute::src')
    if len(file_url)>0 and file_url[0]:
        file_url = file_url[0]
        file_name_only = file_url.split('/')
        file_name_only = file_name_only[len(file_name_only) - 1]
        # 准备保存到本地的完整路径
        file_full_name = './pic/' + dir + '/' + file_name_only

        # 开始下载图片
        Down_load(file_url, file_full_name, 1, 1)
        downloadedPIC +=1
        print('\n已下载图片数量'+str(downloadedPIC))
    nextLink = ''
    if len(html.xpath('//div[@class="pagenavi"]//a[last()]/attribute::href'))>0 and html.xpath('//div[@class="pagenavi"]//a[last()]/span/text()')[0]!='下一组»':
        nextLink = html.xpath('//div[@class="pagenavi"]//a[last()]/attribute::href')[0]
    if  nextLink!='' :
        time.sleep(random.randint(0,1))
        crawler_photo(nextLink,dir)
    



# 将【标准库-阻塞IO实现】替换为【gevent-非阻塞IO实现】
if __name__ == '__main__':

    wall_paper_id = 1
    wall_paper_count = 10
    print("正在下载请稍等……")
    redis_key = input("请输入你的key:")
    gevent.joinall([
        gevent.spawn(crawler_link,'https://www.mzitu.com',wall_paper_count),
        # gevent.spawn(loop_picture),
    ])
    # crawler_link(url,int(wall_paper_count))
    print('\n下载成功!')



