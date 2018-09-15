#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2018 Yida, Personal. All Rights Reserved
# 
########################################################################
 
"""
File: rdf_read.py
Author: yida_915(yida_915@163.com)
Date: 2018/09/15 10:09:15
"""

from rdflib import Graph
import rdflib

g = Graph()
g.parse("demo.nt", format="nt")

print(len(g))

import pprint

for stmt in g:
    pprint.pprint(stmt)

#g.parse("http://bigasterisk.com/foaf.rdf")
#pprint.pprint(g)

