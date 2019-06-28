# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 11:28:37 2019

@author: tianyang.wen
"""

from bs4 import BeautifulSoup
import re
import requests
import os
from tqdm import tqdm

session = requests.Session()
# 创建一个适配器，连接池的数量pool_connections, 最大数量pool_maxsize, 失败重试的次数max_retries
adapter = requests.adapters.HTTPAdapter(pool_connections=100,
                                        pool_maxsize=200, max_retries=3)
# 告诉requests，http协议和https协议都使用这个适配器
session.mount('http://', adapter)
session.mount('https://', adapter)


def list_all_files(rootdir):
    _files = []
    list = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
    for i in range(0, len(list)):
        path = os.path.join(rootdir, list[i])
        if os.path.isdir(path):
            _files.extend(list_all_files(path))
        if os.path.isfile(path):
            _files.append(path)
    return _files


def get_search_urls(input_keyword):
    quanbu_url = 'http://www.youdao.com/example/' + input_keyword + '/#keyfrom=dict.sentence.details.all'
    shumian_url = 'http://www.youdao.com/example/written/' + input_keyword + '/#keyfrom=dict.sentence.details.shumian'
    kouyu_url = 'http://www.youdao.com/example/oral/' + input_keyword + '/#keyfrom=dict.sentence.details.kouyu'
    url_list = [quanbu_url, shumian_url, kouyu_url]
    return url_list


def get_content(single_url):
    source, reference = [], []
    try:
        page_request = session.get(single_url)
        page_request.encoding = 'utf-8'
        page_soup = BeautifulSoup(page_request.text, 'html.parser')
        links = page_soup.find_all('li', attrs={"class": ""})
        for i in links:
            i = i.get_text().strip()
            i = re.sub('\n+', '\n', i).split('\n')
            if len(i) <= 1:
                continue
            source.append(i[0].strip() + '\n')
            reference.append(i[1].strip() + '\n')
    except Exception  as e:
        print(str(e))

    return source, reference


def save_sentences(work_path, urls):
    sum_sentences = 0
    types = ['all_types', 'written', 'oral']
    for i in range(3):
        # import time
        # start = time.time()
        a, b = get_content(urls[i])
        # print(time.time() - start)
        if len(a) > 0 and len(a) == len(b):
            sum_sentences += len(a)
            with open(work_path + types[i] + '_zh.txt', 'a', encoding='utf-8')as f, open(
                    work_path + types[i] + '_en.txt',
                    'a', encoding='utf-8')as f1:
                f.writelines(a)
                f1.writelines(b)
        elif len(a) != len(b):
            print('INFO: Length not same')
        # print(time.time() - start)
    return sum_sentences


def download_sentences_from_single_dict(single_dict, save_path):
    with open(single_dict, 'r', encoding='utf-8')as f:
        zh_dict = f.readlines()
    with open(save_path + 'finished_tasks.txt', 'r', encoding='utf-8')as f:
        a = f.readlines()

    finished_words = set([i.strip() for i in a])
    act_words = set([i.strip() for i in zh_dict]) - finished_words
    ft = []
    import time
    start = time.time()
    for aw in tqdm(act_words):
        # print('INFO: Processing '+str(i+1)+' of '+str(length_dict))
        urls = get_search_urls(aw)
        sum_sentences = save_sentences(save_path, urls)
        if sum_sentences > 0:
            ft.append(aw)

    with open(save_path + 'finished_tasks.txt', 'a', encoding='utf-8')as f:
        f.writelines(ft)
    print(time.time() - start)
    print('########')


def main():
    dict_path = './sougou_dicts'
    save_path = './youdao_sentences/'
    dict_files = list_all_files(dict_path)
    print(dict_files)
    for i in range(len(dict_files)):
        print('INFO: Downloading dict ' + str(i + 1) + ' of ' + str(len(dict_files)))
        if dict_files[i][-4:] != '.txt':
            continue

        download_sentences_from_single_dict(dict_files[i], save_path)


if __name__ == '__main__':
    # from line_profiler import LineProfiler
    #
    # lp = LineProfiler()
    # lp_wrapper = lp(main)
    # lp.print_stats()
    main()
