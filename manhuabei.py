# -*- coding:utf-8 -*-
# !/usr/bin/env python
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
import re
import time
import random
import json

downloadedPIC = 0
random_str = ''
import configparser

cf = configparser.ConfigParser()
cf.read('./config.conf')
datalist = []


# 文件下载器
def Down_load(file_url, file_full_name, now_photo_count, all_photo_count):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        "Referer": "https://www.manhuabei.com/manhua/yirenzhixia/"}

    # 开始下载图片
    with closing(get(file_url, headers=headers, stream=True)) as response:
        chunk_size = 1024  # 单次请求最大值
        content_size = int(response.headers['content-length'])  # 文件总大小
        data_count = 0  # 当前已传输的大小
        with open(file_full_name, "wb") as file:
            for data in response.iter_content(chunk_size=chunk_size):
                file.write(data)
                done_block = int((data_count / content_size) * 50)
                data_count = data_count + len(data)
                now_jd = (data_count / content_size) * 100
                print("\r %s：[%s%s] %d%% %d/%d" % (
                file_full_name, done_block * '█ ', ' ' * (50 - 1 - done_block), now_jd, now_photo_count,
                all_photo_count), end=" ")

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
    # 获取图片列表数据
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        "Referer": "https://www.manhuabei.com/manhua/yirenzhixia/"}
    respond = get(url, headers=headers)
    html = etree.HTML(respond.text)
    photo_data = html.xpath('//ul[@class="list_con_li update_con autoHeight"]/li/a')

    for photo in photo_data:
        dir = photo.xpath('attribute::title')[0]
        dir = re.compile('[!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\s]+').sub('', dir)
        link = photo.xpath('attribute::href')[0]
        loop_picture()


def loop_picture():
    while len(r.lrange(random_str, 0, 4)) > 0:
        result = r.lrange(random_str, 0, 4)
        for photo in result:
            photo = json.loads(photo)
            url = photo['link']
            dir = photo['dir']
            #  创建一个文件夹存放我们下载的图片
            if not exists('./pic/' + str(dir)):
                makedirs('./pic/' + str(dir))
            try:
                gevent.joinall([
                    gevent.spawn(crawler_photo, url, dir),
                ])
            except:
                #    捕获到错误放到队列末尾
                r.rpush(random_str, json.dumps({"dir": dir, "link": url}))
            r.lpop(random_str)


# 爬取不同类型图片
def crawler_photo(url, dir):
    # 获取图片列表数据
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        "Referer": "https://www.manhuabei.com/manhua/yirenzhixia/"}
    respond = get(url, headers=headers)
    html = etree.HTML(respond.text)
    file_url = html.xpath('//img[@class="blur"]/attribute::src')
    if len(file_url) > 0 and file_url[0]:
        file_url = file_url[0]
        file_name_only = file_url.split('/')
        file_name_only = file_name_only[len(file_name_only) - 1]
        # 准备保存到本地的完整路径
        file_full_name = './pic/' + dir + '/' + file_name_only

        # 开始下载图片
        Down_load(file_url, file_full_name, 1, 1)
    nextLink = ''
    if len(html.xpath('//div[@class="pagenavi"]//a[last()]/attribute::href')) > 0 and \
            html.xpath('//div[@class="pagenavi"]//a[last()]/span/text()')[0] != '下一组»':
        nextLink = html.xpath('//div[@class="pagenavi"]//a[last()]/attribute::href')[0]
    if nextLink != '':
        time.sleep(0.5)
        crawler_photo(nextLink, dir)


# 将【标准库-阻塞IO实现】替换为【gevent-非阻塞IO实现】
if __name__ == '__main__':
        name = input('请输入想要看的漫画全名:\n')
        url = 'https://www.manhuadai.com/search/?keywords='+name
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
            "Referer": "https://www.manhuadai.com/manhua/yirenzhixia/"}
        respond = get(url, headers=headers)
        html = etree.HTML(respond.text)
        content_length = html.xpath('//span[@class="comi_num"]/em/text()')[0]
        if int(content_length) < 1:
            print('共查询到'+content_length+'条结果')
        else:
            print('共查询到' + content_length + '条结果')
            should_down = input('是否要全部下载：（Y/N）\n')
            if int(content_length) > 10:
                print('当前选择的漫画数超过10个，下载时间会较长，请耐心等候')
            if should_down== 'Y' or should_down=='y':
                print('正在下载')
                gevent.joinall([
                    gevent.spawn(crawler_link, url),
                ])
        print('\n下载成功!')



