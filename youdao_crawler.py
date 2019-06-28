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

def list_all_files(rootdir):
    _files = []
    list = os.listdir(rootdir) #列出文件夹下所有的目录与文件
    for i in range(0,len(list)):
       path = os.path.join(rootdir,list[i])
       if os.path.isdir(path):
          _files.extend(list_all_files(path))
       if os.path.isfile(path):
          _files.append(path)
    return _files

def get_search_urls(input_keyword):
    quanbu_url = 'http://www.youdao.com/example/' + input_keyword + '/#keyfrom=dict.sentence.details.all'
    shumian_url = 'http://www.youdao.com/example/written/' + input_keyword + '/#keyfrom=dict.sentence.details.shumian'
    lunwen_url = 'http://www.youdao.com/example/paper/' + input_keyword + '/#keyfrom=dict.sentence.details.lunwen'
    kouyu_url = 'http://www.youdao.com/example/oral/' + input_keyword + '/#keyfrom=dict.sentence.details.kouyu'
    url_list=[quanbu_url,shumian_url,lunwen_url,kouyu_url]
    return url_list

def get_content(single_url):
    source,reference=[],[]    
    
    page_request = requests.get(single_url)
    page_request.encoding = 'utf-8'
    page_soup = BeautifulSoup(page_request.text, 'html.parser')
    
    links = page_soup.find_all('li',attrs={"class":""})
    
    for i in links:
        i=i.get_text().strip()
        i=re.sub('\n+','\n',i).split('\n')
        if len(i)<=1:
            continue
        source.append(i[0].strip()+'\n')
        reference.append(i[1].strip()+'\n')
    return source,reference

def save_sentences(workpath,urls):
    sum_sentences=0
    types=['all_types','written','paper','oral']
    for i in range(4):
        a,b=get_content(urls[i])
        if len(a)>0 and len(a)==len(b):
            sum_sentences+=len(a)
            with open(workpath+types[i]+'_zh.txt','a',encoding='utf-8')as f,open(workpath+types[i]+'_en.txt','a',encoding='utf-8')as f1:
                f.writelines(a)
                f1.writelines(b)
        elif len(a)!=len(b):
            print('INFO: Length not same')    
    return sum_sentences

def download_sentences_from_single_dict(single_dict,savepath):
    with open(single_dict,'r',encoding='utf-8')as f:
        zh_dict=f.readlines()
    with open(savepath+'finished_tasks.txt','r',encoding='utf-8')as f:
        a=f.readlines()
        
    finished_words=[i.strip() for i in a]
    length_dict=len(zh_dict)
    
    for i in tqdm(range(length_dict)):
        #print('INFO: Processing '+str(i+1)+' of '+str(length_dict))
        if zh_dict[i].strip() in finished_words:
            continue    
        urls=get_search_urls(zh_dict[i].strip())
        sum_sentences=save_sentences(savepath,urls)
        if sum_sentences>0:
            with open(savepath+'finished_tasks.txt','a',encoding='utf-8')as f:
                f.writelines(zh_dict[i])
def main():
    dict_path='./sougou_dicts'
    save_path='./youdao_sentences/'
    
    dict_files=list_all_files(dict_path)
    
    for i in range(len(dict_files)):
        print('INFO: Downloading dict '+str(i+1)+' of '+str(len(dict_files)))
        if dict_files[i][-4:]!='.txt':
            continue
        download_sentences_from_single_dict(dict_files[i],save_path)

if __name__=="__main__":
    main()     
           



