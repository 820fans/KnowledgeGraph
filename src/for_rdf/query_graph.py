#!/usr/bin/env python
# -*- coding: utf-8 -*
########################################################################
# 
# Copyright (c) 2018 Yida, Personal. All Rights Reserved
# 
########################################################################

"""
File: create_graph.py
Author: yida_915(yida_915@163.com)
Date: 2018/09/16 22:03:22
"""

from rdflib import URIRef, BNode, Literal
from rdflib import Namespace
from rdflib import Graph
from rdflib.namespace import RDF, FOAF
import pprint
from urllib.parse import quote
import string
import time

author_map = {}
affi_map = {}

g = Graph()


class CreateGraph:

    def init_set(self, ):
        with open("./affiliation_set.txt") as f:
            for line in f:
                line = line.strip()
                items = line.split("\t")
                affi_no, affi_name = items[0], items[1]
                affi_map[affi_name] = affi_no

    def safe_add(self, rdf_obj):
        if rdf_obj not in g:
            g.add(rdf_obj)


if __name__ == "__main__":
    aca_au = Namespace("http://yida.academic.org/author/")
    aca_af = Namespace("http://yida.academic.org/affiliation/")

    cg = CreateGraph()
    cg.init_set()

    st=time.clock()
    g.parse("author_graph.rdf", format="n3")

# <http://yida.academic.org/affiliation/No.50149> a ns1:Affiliation ;
#     ns1:name "化工过程模拟与优化教育部工程研究中心,411105" .
    qres = g.query(
        """
        Prefix relation: <http://xmlns.com/foaf/0.1/>
        Prefix affi: <http://yida.academic.org/affiliation/>
        SELECT ?author_name WHERE { 
        ?author relation:workIn affi:No.103419 .
        ?author relation:name ?author_name
        }
        """)
    md=time.clock()
    for row in qres:
        print(row[0])
    ed=time.clock()
    print(md-st)
    print(ed-md)
