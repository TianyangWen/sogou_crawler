# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 18:13:35 2019

@author: tianyang.wen
"""

import os
import re
from urllib.parse import unquote

import requests
from tqdm import tqdm


def list_all_files(rootdir):
    _files = []
    list = os.listdir(rootdir)  #列出文件夹下所有的目录与文件
    for i in range(0, len(list)):
        path = os.path.join(rootdir, list[i])
        if os.path.isdir(path):
            _files.extend(list_all_files(path))
        if os.path.isfile(path):
            _files.append(path)
    return _files


def download_single_category(input_txt):
    with open(input_txt, 'r', encoding='utf-8') as f:
        urls = f.readlines()
    cate_name = re.sub('.*dict_download_urls/', '', input_txt[:-4])
    os.mkdir('./download_scels/' + cate_name)
    for i in tqdm(urls):
        url = i[:-1]
        page_request = requests.get(url)
        dict_name = unquote(re.sub('.*name=', '', url), 'utf-8')
        dict_name = re.sub('/', '', dict_name)  #防止词典名中有斜杠，识别为路径
        with open('./download_scels/' + cate_name + '/' + dict_name + '.scel',
                  "wb") as code:
            code.write(page_request.content)

def main():
    url_filenames = list_all_files('./dict_download_urls')

    for file in url_filenames:
        print('INFO:Processing ' + str(file + 1) + ' of ' +
            str(len(url_filenames)))
        if file[-4:] == '.txt':
            download_single_category(file)

if __name__ == "__main__":
    main()
