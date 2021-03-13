# -*- coding:utf-8 -*-

from requests import get
from filetype import guess
from os import rename
from os import makedirs
from os.path import exists
from json import loads
from contextlib import closing
from lxml import etree
downloadedPIC = 0
# 文件下载器
def Down_load(file_url, file_full_name, now_photo_count, all_photo_count):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}

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
    file_type = guess(file_full_name)
    rename(file_full_name, file_full_name)



# 爬取不同类型图片
def crawler_photo(url,num):
    #一页默认只有10张
    type_id = 1
    global downloadedPIC
    # 获取图片列表数据
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}
    respond = get(url, headers=headers)
    html = etree.HTML(respond.text)
    # print(html)
    photo_data = html.xpath('//ol[@class="commentlist"]//a[@class="view_img_link"]/attribute::href')
    # 已经下载的图片张数
    now_photo_count = 1
    # 所有图片张数
    all_photo_count = len(photo_data)
    # 开始下载并保存5K分辨率壁纸
    for photo in photo_data:

        # 创建一个文件夹存放我们下载的图片
        if not exists('./' + str(type_id)):
            makedirs('./' + str(type_id))

        # 准备下载的图片链接
        file_url = "http:" + photo
        # 准备下载的图片名称,不包含扩展名
        file_name_only = file_url.split('/')
        file_name_only = file_name_only[len(file_name_only) - 1]
        
        # 准备保存到本地的完整路径
        file_full_name = './' + str(type_id) + '/' + file_name_only

        # 开始下载图片
        Down_load(file_url, file_full_name, now_photo_count, all_photo_count)
        downloadedPIC += 1
    if downloadedPIC < num :
        # 已经下载的数量如果不够就递归下载下一页
        crawler_photo('http:'+html.xpath('//a[@class="previous-comment-page"]/attribute::href')[0],num)
    




if __name__ == '__main__':

    # 最新 1, 最热 2, 女生 3, 星空 4
    # 爬取类型为3的图片(女生),一共准备爬取20000张
    wall_paper_id = 1
    wall_paper_count = 10
    # 换行符
    print('\n\n')
    # 选择要下载的壁纸数量
    wall_paper_count = input("请输入要下载的数量：")
    # 判断输入是否正确
    while(int(wall_paper_count) <= 0):
        wall_paper_count = input("请输入要下载的数量：")


    # 开始爬取5K高清壁纸
    print("正在下载请稍等……")
    url='http://jandan.net/ooxx'
    crawler_photo(url,int(wall_paper_count))
    print('\n下载成功!')



