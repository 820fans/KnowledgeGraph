#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2018 Yida, Personal. All Rights Reserved
# 
########################################################################

"""
File: wash_json_one_affi.py
Author: yida_915(yida_915@163.com)
Date: 2018/08/28 22:10:47
"""

import sys
import json
from neomodel import config

# config.DATABASE_URL = 'bolt://neo4j:neo4j@localhost:7687'  # default

from neomodel import db

db.set_connection('bolt://neo4j:237200zw@localhost:7687')

from neomodel import (config, StructuredNode, StringProperty, IntegerProperty,
                      FloatProperty, UniqueIdProperty, RelationshipTo, RelationshipFrom,
                      ArrayProperty,
                      StructuredRel, DateTimeProperty)
from neomodel import cardinality
import neomodel

class WorkInRel(StructuredRel):
    # 置信度, 作者属于该机构的置信度
    # 当论文机构数量>1时, 每个作者具备置信度1/n, 表示这条链接属性的置信度
    rel_credibility = FloatProperty(default=1)


class Affiliation(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    # 一个机构里面可以有多个作者
    has_authors = RelationshipFrom('Author', 'WORK_IN', model=WorkInRel)

    def safe_save(self):
        if Affiliation.nodes.get_or_none(name=self.name) is None:
            return self.save()
        else:
            return Affiliation.nodes.get(name=self.name)

class Author(StructuredNode):
    # uid = UniqueIdProperty()
    name = StringProperty(unique_index=True)
    age = IntegerProperty(index=True, default=0)
    birthday = DateTimeProperty()
    birth_place = StringProperty()

    # 由于重名问题的存在, 一个作者可能属于多个机构
    affiliation = RelationshipTo('Affiliation', 'WORK_IN', model=WorkInRel)
    publish = RelationshipTo('Paper', 'Publish')
    # 一个作者会和多个作者合作.
    co_authors = RelationshipTo('Author', 'CO_AUTHOR')
    coed_authors = RelationshipFrom('Author', 'CO_AUTHOR')
    # 作者重名问题, 判断摘要keywords的相似度, 相似度高则认为是同一作者
    # 判断机构是否和已有的作者一致.

    def safe_save(self):
        if Author.nodes.get_or_none(name=self.name) is None:
            return self.save()
        else:
            return Author.nodes.get(name=self.name)

    def safe_co_link(self, author_instance):
        if not self.co_authors.is_connected(author_instance):
            self.co_authors.connect(author_instance)

    def safe_write_link(self, paper_instance):
        if not self.publish.is_connected(paper_instance):
            self.publish.connect(paper_instance)

    def safe_af_link(self, affi_instance, rel_credibility):
        if not self.affiliation.is_connected(affi_instance):
            self.affiliation.connect(affi_instance,
                                      {'rel_credibility': rel_credibility})


class Literature(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    UniqueIdProperty()
    # 中图文分类号
    clc_types = ArrayProperty(StringProperty())
    has_papers = RelationshipFrom('Paper', 'Publish_AT')

    def safe_save(self):
        if Literature.nodes.get_or_none(name=self.name) is None:
            return self.save()
        else:
            return Literature.nodes.get(name=self.name)

class Paper(StructuredNode):
    name = StringProperty(unique_index=True, required=True)

    abstract = StringProperty(default="")
    keywords = ArrayProperty(StringProperty())
    authors = ArrayProperty(StringProperty())

    publish_time_str = StringProperty
    publish_time = DateTimeProperty()
    published_at = RelationshipTo('Literature', 'Publish_AT')
    published_by = RelationshipFrom('Author', 'Publish_BY')

    def safe_save(self):
        if Paper.nodes.get_or_none(name=self.name) is None:
            return self.save()
        else:
            return Paper.nodes.get(name=self.name)


    def safe_publish_link(self, literal_instance):
        if not self.published_at.is_connected(literal_instance):
            self.published_at.connect(literal_instance)

data_arr = []
with open("spider/data_TP31.dat") as f:
    for line in f:
        line = line.strip()
        if len(line) == 0: continue

        paper = json.loads(line)
        data = {}
        data['title'] = paper['Title']
        data['authors'] = paper['Authors']
        data['affiliations'] = paper['AuthorsAffiliations']
        data['subjects'] = paper['Subjects']
        data['abstract'] = paper['Abstract']
        data['year'] = str(paper['Year'])
        data['literature'] = paper['Literature']
        data['clc'] = paper['CLC']
        data_arr.append(data)

# print(data_arr)
import pandas as pd

paper_df = pd.DataFrame(data_arr)


for index, row in paper_df.iterrows():
    paper_item = Paper(name=row['title'], abstract=row['abstract'],
                       keywords=row['subjects'], authors=row['authors'],
                       publish_time_str=row['year'])
    paper_item = paper_item.safe_save()
    authors = []
    for author in row['authors']:
        author_item = Author(name=author, age=20)
        author_item = author_item.safe_save()
        authors.append(author_item)
    # 合作网络
    for i in authors:
        for j in authors:
            if i != j:
                i.safe_co_link(j)
                j.safe_co_link(i)

    affiliations = []
    for affiliation in row['affiliations']:
        affiliation = affiliation.split(",")[0]
        affiliation_item = Affiliation(name=affiliation)
        affiliation_item = affiliation_item.safe_save()
        affiliations.append(affiliation_item)

    # 机构网络
    temp_rel_credibility = 1.0/ (len(affiliations)*1.0)
    for i in authors:
        for j in affiliations:
            i.safe_af_link(j, temp_rel_credibility)
    # 发表论文
    for i in authors:
        i.safe_write_link(paper_item)

    # 期刊名称
    literature_name = row['literature']
    literature_item = Literature(name=literature_name, clc_types=row['clc'])
    literature_item = literature_item.safe_save()
    # 发表网络
    paper_item.safe_publish_link(literature_item)

    # break
# print(paper_df.head())
