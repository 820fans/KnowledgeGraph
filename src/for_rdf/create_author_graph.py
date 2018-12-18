#!/usr/bin/env python
# -*- coding: utf-8 -*
########################################################################
# 
# Copyright (c) 2018 Yida, Personal. All Rights Reserved
# 
########################################################################

"""
File: create_author_graph.py
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

    def init_set(self,):
        with open("./70w_author_set_no.txt") as f:
            for line in f:
                line = line.strip("\t\r\n")
                items = line.split("\t")
                au_no, author_name = items[0], items[1]
                author_map[author_name] = au_no

        with open("./70w_affi_set_no.txt") as f:
            for line in f:
                line = line.strip("\t\r\n")
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

    # 开始时间
    start_time = time.clock()
    g.parse("au_af_graph.rdf", format="n3")

    middle_time = time.clock()
    qres = g.query(
            """   
            Prefix relation: <http://xmlns.com/foaf/0.1/>
            Prefix affi: <http://yida.academic.org/affiliation/>
            SELECT ?author_name WHERE { 
            ?author relation:workIn affi:No.124348 .
            ?author relation:name ?author_name
            }
            """)

    for row in qres:
        print(row[0])
    end_time = time.clock()

    print("graph loading time:" + str(middle_time - start_time))
    print("query time:" + str(end_time - middle_time))

"""
    with open("./author_affi_pair.txt") as f:
        for line in f:
            items = line.strip().split("\t")
            author, affi = items[0], items[1]

            if author not in author_map: continue
            if affi not in affi_map: continue

            author_id = "No." + str(author_map[author]) + ""
            affi_id = "No." + str(affi_map[affi]) + ""

            au = URIRef(aca_au[author_id])
            af = URIRef(aca_af[affi_id])

            if (au, RDF.type, FOAF.Author) not in g:
                g.add((au, RDF.type, FOAF.Author))
            if (au, FOAF.name, Literal(author)) not in g:
                g.add((au, FOAF.name, Literal(author)))

            g.add((af, RDF.type, FOAF.Affiliation))
            g.add((af, FOAF.name, Literal(affi)))

            g.add((au, FOAF.workIn, af))

        g.serialize(destination="author_graph.rdf", format="turtle")
"""