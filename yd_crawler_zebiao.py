# -*- coding: utf-8 -*-
"""
 Created by zaber on 2018-11-27 11:
"""

import os
import signal
import sys
import re
from multiprocessing import Process, Queue, Manager

text_process = Queue()
processed = Queue()
processed_word = Queue()
man = Manager()

name = man.dict({'ok': False})
save_path = './youdao_sentences111/'
dict_path = './sougou_dicts11'


class ProcessThread(Process):
    def __init__(self, device='-1', n='ProcessThread', sp='', dp=''):
        super(ProcessThread, self).__init__(name=n)
        self.name = n + device
        self.device = device
        self.save_path = sp
        self.dict_path = dp

    @staticmethod
    def get_search_urls(input_keyword):
        quanbu_url = 'http://www.youdao.com/example/' + input_keyword + '/#keyfrom=dict.sentence.details.all'
        shumian_url = 'http://www.youdao.com/example/written/' + input_keyword + '/#keyfrom=dict.sentence.details.shumian'
        kouyu_url = 'http://www.youdao.com/example/oral/' + input_keyword + '/#keyfrom=dict.sentence.details.kouyu'
        url_list = [quanbu_url, shumian_url, kouyu_url]
        return url_list

    @staticmethod
    def get_content(single_url):
        from bs4 import BeautifulSoup
        import requests
        source, reference = [], []
        page_request = requests.get(single_url)
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
        return source, reference

    def save_sentences(self, urls):
        sum_sentences = 0
        types = ['all_types', 'written', 'oral']
        for i in range(3):
            # import time
            # start = time.time()
            a, b = self.get_content(urls[i])
            # print(time.time() - start)
            if len(a) > 0 and len(a) == len(b):
                sum_sentences += len(a)
                processed.put((types[i], a, b))
            elif len(a) != len(b):
                print('INFO: Length not same')
        return sum_sentences

    def run(self):
        print(self.name, os.getpid())

        ok = False
        while not ok:
            if not text_process.empty():
                # print('not process[setting.TEXT_INSTANCE].empty():')
                zh_dict, finished_words = text_process.get()
                zh_dict = zh_dict.strip()
                if zh_dict in finished_words:
                    continue
                urls = self.get_search_urls(zh_dict)
                sum_sentences = self.save_sentences(urls)
                if sum_sentences > 0:
                    processed_word.put(zh_dict)
                ok = name['ok']


class Model(object):
    def __init__(self):
        pass

    @staticmethod
    def process(single_dict, finished_words):
        print('running')
        with open(single_dict, 'r', encoding='utf-8')as f:
            zh_dict = f.readlines()

        for i in zh_dict[:200]:
            text_process.put((i, finished_words))
            # print('INFO: Processing '+str(i+1)+' of '+str(length_dict))
        done = False
        size = 10000000000
        while not done:

            prd_size = text_process.qsize()

            if prd_size == 0:
                print('It is ok !')
                done = True
            elif size > prd_size:
                # logging.info(self.name, self.instance, ' alive')
                print('剩余处理任务集合 :%s ' % prd_size)
                size = prd_size

        while not processed.empty():
            types, a, b = processed.get()
            fa = save_path + types + '_zh.txt'
            fb = save_path + types + '_en.txt'
            with open(fa, 'a', encoding='utf-8')as f, open(fb, 'a', encoding='utf-8')as f1:
                f.writelines(a)
                f1.writelines(b)

        zh = []
        while not processed_word.empty():
            zh.append(processed_word.get())
        with open(save_path + 'finished_tasks.txt', 'a', encoding='utf-8')as f:
            f.writelines(zh)


def process_quit(signum, frame):
    print('You choose to stop me. %s %s' % (str(signum), str(frame)))
    print('current pid is %s, group id is %s' % (os.getpid(), os.getpgrp()))
    os.killpg(os.getpgid(os.getpid()), signal.SIGKILL)
    name['ok'] = True
    sys.exit(-1)


sub_thread = []
for gid in range(5):
    st = ProcessThread(sp=save_path, dp=dict_path, device=str(gid))
    st.daemon = True
    sub_thread.append(st)
    st.start()


def list_all_files(rootdir):
    _files = []
    lists = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
    for i in range(0, len(lists)):
        path = os.path.join(rootdir, lists[i])
        if os.path.isdir(path):
            _files.extend(list_all_files(path))
        if os.path.isfile(path):
            _files.append(path)
    return _files


def main():
    dict_files = list_all_files(dict_path)
    print(dict_files)
    m = Model()
    for i in range(len(dict_files)):
        print('INFO: Downloading dict ' + str(i + 1) + ' of ' + str(len(dict_files)))
        if dict_files[i][-4:] != '.txt':
            continue
        with open(save_path + 'finished_tasks.txt', 'r', encoding='utf-8')as f:
            a = f.readlines()
        finished_words = set([i.strip() for i in a])
        m.process(dict_files[i], finished_words)
    name['ok'] = True


if __name__ == '__main__':
    import time

    start = time.time()
    main()
    print(time.time() - start)
