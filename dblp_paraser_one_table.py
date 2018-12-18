#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import importlib,sys
importlib.reload(sys)
import xml.sax
import re
# import mysql_util
# from mysql_util import mysqlutil
# import MySQLdb
import codecs

#paper_tags = ('article','inproceedings','proceedings','book', 'incollection','phdthesis','mastersthesis','www')
paper_tags = ('article','inproceedings') ## only parse these tags
sub_tags = ('publisher', 'journal', 'booktitle')

sqlf = codecs.open("dblp-py.sql", "w", "utf-8")

class MovieHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.id = 1
        self.kv = {}
        self.reset()
        self.params = []
        self.batch_len = 10

    def reset(self):
        self.curtag = None
        self.pid = None
        self.ptag = None
        self.title = None
        self.author = None
        self.tag = None
        self.subtag = None
        self.subtext = None
        self.year = None
        self.url = None
        self.mdate = None
        self.key = None
        self.publtype = None
        self.kv = {}

    #元素开始事件处理
    def startElement(self, tag, attributes):
        if tag is not None and len(tag.strip()) > 0:
            self.curtag = tag

            if tag in paper_tags:
                self.reset()
                self.pid = self.id
                self.kv['ptag'] = str(tag)
                self.kv['id'] = self.id
                self.id += 1

                if 'key' in attributes:
                    self.key = str(attributes['key'])

                if 'mdate' in attributes:
                    self.mdate = str(attributes['mdate'])

                if 'publtype' in attributes:
                    self.publtype = str(attributes['publtype'])
            elif tag in sub_tags:
                self.kv['sub_tag'] = str(tag)

    # 元素结束事件处理
    def endElement(self, tag):
        if tag == 'title':
            self.kv['title'] = str(self.title)

        elif tag == 'author':
            self.author = re.sub(' ','_', str(self.author))
            if 'author' not in self.kv:
                self.kv['author'] = []
                self.kv['author'].append(str(self.author))
            else:
                self.kv['author'].append(str(self.author))

        elif tag in sub_tags:
            self.kv['sub_detail'] = str(self.subtext)

        elif tag == 'url':
            self.kv['url'] = str(self.url)

        elif tag == 'year':
            self.kv['year'] = str(self.year)

        elif tag in paper_tags:
            tid = int(self.kv['id']) if 'id' in self.kv else 0
            ptag = self.kv['ptag'] if 'ptag' in self.kv else 'NULL'

            try:
                title = self.kv['title'] if 'title' in self.kv else 'NULL'
            except:
                title = ''
            author = self.kv['author'] if 'author' in self.kv else 'NULL'
            author = ','.join(author) if author is not None else 'NULL'
            subtag = self.kv['subtag'] if 'subtag' in self.kv else 'NULL'
            sub_detail = self.kv['sub_detail'] if 'sub_detail' in self.kv else 'NULL'
            year = self.kv['year'] if 'year' in self.kv else 0
            url = self.kv['url'] if 'url' in self.kv else 'NULL'
            mdate = self.kv['mdate'] if 'mdate' in self.kv else 'NULL'
            pkey = self.kv['pkey'] if 'pkey' in self.kv else 'NULL'
            publtype = self.kv['publtype'] if 'publtype' in self.kv else 'NULL'
            param = (str(tid), ptag, title, author, subtag, sub_detail, year, url, mdate, pkey, publtype)

            # 只抽取其中的会议论文
            if url.find('db/conf') >= 0:
                self.params.append(param)

            if len(self.params) % self.batch_len == 0:
                # print(len(self.params))
                if len(self.params) > 0:
                #     print(self.params)
                    prams = self.params
                    sqlf.write("insert into paper_conf(id, ptag, title, author, subtag, sub_detail, year, url, mdate, pkey, publtype) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);" \
                               % param)
                    sqlf.write("\n")
                # sql = "insert into paper_conf(id, ptag, title, author, subtag, sub_detail, year, url, mdate, pkey, publtype) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                # self.util.execute_sql_params(sql, self.params)
                self.params = []

    # 内容事件处理
    def characters(self, content):
        if self.curtag == "title":
            self.title = content.strip()
        elif self.curtag == "author":
            self.author = content.strip()
        elif self.curtag in sub_tags:
            self.subtext = content.strip()
        elif self.curtag == "year":
            self.year = content.strip()
        elif self.curtag == "url":
            self.url = content.strip()

## python parser.py dblp.xml
if __name__ == "__main__":

    filename = 'test.xml'
    if len(sys.argv) == 2:
        filename = sys.argv[1]

    if os.path.exists(filename) == False:
        print('[%s] not exists!' % filename)
        exit(1)

    # 创建一个 XMLReader
    parser = xml.sax.make_parser()

    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    # 重写 ContextHandler
    Handler = MovieHandler()
    parser.setContentHandler( Handler )

    parser.parse(filename)
    print('Parser Complete!')
