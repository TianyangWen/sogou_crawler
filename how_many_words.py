# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 14:32:58 2019

@author: tianyang.wen
"""

import os


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


workpath = '/root/sogou_crawler/sougou_dicts'
a = list_all_files(workpath)
length_words = 0
for i in a:
    with open(i, 'r', encoding='utf-8') as f:
        aaa = f.readlines()
    length_words += len(aaa)
print(length_words)
