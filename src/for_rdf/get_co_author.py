#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2018 Yida, Personal. All Rights Reserved
# 
########################################################################

"""
File: get_co_author.py
Author: yida_915(yida_915@163.com)
Date: 2018/09/19 20:09:46
"""

import sys
import re

for line in sys.stdin:
    line = line.strip("\t\r\n")
    items = line.split('\t')
    if len(items) != 8: continue
    authors, affi = items[1], items[2]
    authors = authors.split("|")
    # 多机构的过滤掉
    if len(affi.split("|")) > 1: continue
    for item in authors:
        # 过滤拼音英文的姓名
        res = re.search('[a-zA-Z]', item)
        if res == None:
            affis = affi.split(",")[0]
            # 过滤非汉字
            if all('\u4e00' <= char <= '\u9fff' for char in item):
                print("|".join([item, affis]))
