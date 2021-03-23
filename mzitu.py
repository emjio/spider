# -*- coding:utf-8 -*-
#!/usr/bin/env python
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
import json
fp = 'config.conf'
# r = redis.Redis(connection_pool=pool)
import copy
import re
import time
import random
import json
import logging
downloadedPIC = 0
random_str = ''
import configparser
cf = configparser.ConfigParser()
cf.read('./config.conf')
datalist = []
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
                print("\r %s：[%s%s] %d%% %d/%d" % (file_full_name, done_block * '█ ', ' ' * (50 - 1 - done_block), now_jd, now_photo_count, all_photo_count), end=" ")

    # 下载完图片后获取图片扩展名，并为其增加扩展名
    # file_type = guess(file_full_name)
    rename(file_full_name, file_full_name)

#
def generate_random_str(randomlength=16):
  """
  生成一个指定长度的随机字符串
  """
  random_str = ''
  base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
  length = len(base_str) - 1
  for i in range(randomlength):
    random_str += base_str[random.randint(0, length)]
  return random_str

def crawler_link(url):
    global  datalist
    print('当前已获取条目数量'+str(len(datalist)))
    # 获取图片列表数据
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36","Referer":"https://www.mzitu.com/"}
    respond = get(url, headers=headers)
    html = etree.HTML(respond.text)
    photo_data = html.xpath('//ul[@id="pins"]/li/a[1]')
    # 已经下载的图片张数
    nextLink= ''
    if len(html.xpath('//a[@class="next page-numbers"]'))>0 :
        nextLink = html.xpath('//a[@class="next page-numbers"]/attribute::href')[0]
    # 开始下载并保存5K分辨率壁纸
    for photo in photo_data:
        dir = photo.xpath('img/attribute::alt')[0]
        dir =  re.compile('[!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\s]+').sub('',dir)
        link = photo.xpath('attribute::href')[0]
        datalist.append({"dir":dir,"link":link})
    if  nextLink!='' :
        # time.sleep(0.2)
        crawler_link(nextLink)
    else:
        save_data()
        cf.set('str', 'list_finish', 'true')
        with open(fp, 'w') as fw:
            cf.write(fw)
        print('全站已经采集完毕共计'+str(len(datalist)))
        data = open('./datalist.txt', mode='r')
        data = data.read()
        datalist = data.split('\n')
        loop_picture()

def save_data():
    data = open('./datalist.txt', mode='w+')
    str_datalist = '\n'.join(json.dumps(item) for item in datalist)
    data.write(str_datalist)
    data.close()
def loop_picture():
    global  datalist
    while len(datalist) > 0:
        copy_result = copy.deepcopy(datalist[0:4])
        for photo in copy_result:
            print(photo)
            photo = json.loads(photo)
            url = photo['link']
            dir = photo['dir']
            #  创建一个文件夹存放我们下载的图片
            if not exists('./pic/' + str(dir)):
                makedirs('./pic/' + str(dir))
            try:
                 gevent.joinall([
                     gevent.spawn(crawler_photo,url,dir),
                 ])
            except:
             #    捕获到错误放到队列末尾
                 datalist.append(json.dumps({"dir": dir, "link": url}))
            datalist.pop(0)
            save_data()

    
# 爬取不同类型图片
def crawler_photo(url,dir):
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

        # 开始下载图片da
        Down_load(file_url, file_full_name, 1, 1)
    nextLink = ''
    if len(html.xpath('//div[@class="pagenavi"]//a[last()]/attribute::href'))>0 and html.xpath('//div[@class="pagenavi"]//a[last()]/span/text()')[0]!='下一组»':
        nextLink = html.xpath('//div[@class="pagenavi"]//a[last()]/attribute::href')[0]
    if  nextLink!='' :
        time.sleep(0.5)
        crawler_photo(nextLink,dir)
    



# 将【标准库-阻塞IO实现】替换为【gevent-非阻塞IO实现】
if __name__ == '__main__':
    if cf.has_option('str','random_str'):
        random_str = cf.get("str", "random_str")
    else:
        random_str = generate_random_str()
        cf.set('str','random_str',random_str)
        with open(fp, 'w') as fw:
            cf.write(fw)
    if cf.has_option('str','list_finish'):
        print('您已经采集过目录了，正在恢复到上一次的进度。。。')
        data = open('./datalist.txt',mode='r')
        data = data.read()
        datalist = data.split('\n')
        gevent.joinall([
            gevent.spawn(loop_picture),
        ])
    else:
        print('正在开始采集数据目录，此阶段大约需要10分钟，请勿退出或关闭窗口')
        gevent.joinall([
            gevent.spawn(crawler_link, 'https://www.mzitu.com'),
        ])
    print('\n下载成功!')



