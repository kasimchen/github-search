# -*- coding: utf-8 -*-
import urllib
import urllib2
import requests
import re
from lxml import etree #引入xpath解析
import codecs
import  sys
import threading,time
from time import sleep, ctime

#第一次写python 请指教哈！

reload(sys)
sys.setdefaultencoding('utf-8')

def fetch_list(page,nsec):
        print '<-------开始读取第'+str(page)+'页------->'
        url = 'https://github.com/search?p='+str(page)+'&q=bilibili&type=Repositories&utf8=%E2%9C%93'
        data = get_page_data(url)
        write_to_file(data)
        sleep(nsec)

#获取列表资料
def get_page_data(url):

    r = requests.get(url, allow_redirects=False)
    if(r.status_code != requests.codes.ok):
        print '<-------采集结束------->'
        exit(0)

    selector = etree.HTML(r.content)
    content = selector.xpath('//*[@class="column three-fourths codesearch-results"]/ul/li')

    pagelist = []

    if content:
        print '<-------获取资料成功------->'
        for each in content:
            link = each.xpath('div/h3/a/@href')[0]
            title = each.xpath('div/h3/a/text()')[0]

            print url

            # 过滤没有描述的项目
            if not each.xpath('p/text()'):
                description = ''
            else:
                description = each.xpath('p/text()')[0]

            # 过滤没有分类的项目
            if not each.xpath('div[@class="f6 text-gray mt-2"]/span/text()'):
                type = ''
            else:
                type = each.xpath('div[@class="f6 text-gray mt-2"]/span/text()')[0]

            # 过滤没有start的项目
            if not each.xpath('div[@class="f6 text-gray mt-2"]/a[1]/text()'):
                start = '0'
            else:
                start = each.xpath('div[@class="f6 text-gray mt-2"]/a[1]/text()')[1]

            #单页

            single_data = get_single_data('https://github.com'+str(link));
            body = single_data[0]
            download_url = single_data[1]

            list = [link, title, description,type,start,body,download_url]
            pagelist.append(list)
        print '<-------资料解析成功------->'
    return pagelist

#获取单页文本信息
def get_single_data(url):
    r = requests.get(url, allow_redirects=False)
    print  url
    content = re.findall('<article class="markdown-body entry-content" itemprop="text">(.*?)</article>',r.content,re.S)
    download_url = url+'/archive/master.zip'

    if not content:
        body = ''
    else:
        body = content[0]
    data = [body,download_url]
    return data



#写入至file
def write_to_file(pagelist):

    # 新建文件写入结果
    new_path_filename = "dh_list.txt"
    f = codecs.open(new_path_filename, 'a', 'utf-8')

    for dh in pagelist:

        insert_str = str(dh[0]) + ' ' \
                     + str(dh[1]) + ' ' \
                     + str(dh[2]) + ' ' \
                     + str(dh[3]) +' '\
                     + str(dh[4]) + ' ' \
                     +str(dh[5]) + ' ' \
                     + str(dh[6]) + ' ' \
                     + '\n'
        print insert_str
        f.write(insert_str)
    f.close()
    print '<-------写入成功------->'


#多线程处理
def main():
    threadpool=[]
    for i in range(0,5,1):
        th = threading.Thread(target= fetch_list,args=(i,2))
        threadpool.append(th)

    for th in threadpool:
        th.setDaemon(True)
        th.start()
    th.join()
    print "all over %s" %ctime()

if __name__ == '__main__':
        main()