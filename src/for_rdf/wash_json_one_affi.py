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

for line in sys.stdin:
    line = line.strip()
    if len(line) == 0: continue

    paper = json.loads(line)
    title = paper['Title']
    authors = '|'.join(paper['Authors'])
    affiliations = '|'.join(paper['AuthorsAffiliations'])
    subjects = '|'.join(paper['Subjects'])
    abstract = paper['Abstract']
    year = str(paper['Year'])
    literature = paper['Literature']
    clc = '|'.join(paper['CLC'])

    # 统计作者vs机构
    authors_len = len(authors.split("|"))
    affiliations_len = len(affiliations.split("|"))
    if affiliations_len > 1:
        continue

    print("\t".join([title, authors, affiliations, subjects, abstract, year,
                     literature, clc]))
