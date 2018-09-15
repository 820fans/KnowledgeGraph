#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2018 Yida, Personal. All Rights Reserved
# 
########################################################################
 
"""
File: rdf_create.py
Author: yida_915(yida_915@163.com)
Date: 2018/09/15 10:32:19
"""

from rdflib import URIRef, BNode, Literal
from rdflib import Namespace
from rdflib.namespace import RDF, FOAF

people = Namespace("http://yida.artitect.org/people/")
bob = URIRef("http://example.org/people/Bob")
linda = BNode() # a GUID is generated

name = Literal('贾斯汀 Bob') # passing a string
age = Literal(24) # passing a python int
height = Literal(76.5) # passing a python float

print(RDF.type)
print(FOAF.knows)

