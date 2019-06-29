# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 16:08:00 2019

@author: tianyang.wen
"""

import re

import requests
from bs4 import BeautifulSoup


def get_main_categories():
    base_url = 'https://pinyin.sogou.com/dict/'
    page_request = requests.get(base_url)
    page_request.encoding = 'utf-8'
    page_soup = BeautifulSoup(page_request.text, 'html.parser')

    links = page_soup.find_all('div',
                               attrs={"class": "dict_category_list_title"})
    main_categories = []
    for link in links:
        complex_link = base_url + link.a.attrs['href'][6:]
        main_categories.append(re.sub('\?.*', '', complex_link))
    return main_categories


def detect_download_links(input_url):
    page_request = requests.get(input_url)
    page_request.encoding = 'utf-8'
    page_soup = BeautifulSoup(page_request.text, 'html.parser')
    links = page_soup.find_all('div', attrs={"class": "dict_dl_btn"})
    #names = page_soup.find_all('div',attrs={"class":"detail_title"})
    download_links = []
    for link in links:
        download_links.append(link.a.attrs['href'] + '\n')
    return download_links


def collect_urls(single_category):
    download_links = []
    for i in range(2000):
        new_links = detect_download_links(single_category + '/default/' +
                                          str(i + 1))
        if new_links:
            download_links += new_links
        else:
            break
    with open('./dict_download_urls/' + single_category[41:] + '.txt',
              'w',
              encoding='utf-8') as f:
        f.writelines(download_links)
    print('INFO:Collected ' + str(len(download_links)) + ' urls')


categories = get_main_categories()
extend_categories = [
    'https://pinyin.sogou.com/dict/cate/index/180',  #北京
    'https://pinyin.sogou.com/dict/cate/index/366',  #国外
    'https://pinyin.sogou.com/dict/cate/index/306',  #上海
    'https://pinyin.sogou.com/dict/cate/index/330',  #香港
    'https://pinyin.sogou.com/dict/cate/index/318',  #台湾
]
categories += extend_categories

for i in range(len(categories)):
    print('INFO:Processing ' + str(i + 1) + ' of ' + str(len(categories)))
    collect_urls(categories[i])
