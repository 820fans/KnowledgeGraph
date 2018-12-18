# -*- coding: UTF-8 -*-

from rdflib import URIRef, BNode, Literal
from rdflib import Namespace
from rdflib import Graph
from rdflib.namespace import RDF, FOAF
import pprint
from urllib.parse import quote
import string

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

    with open("./co_author_set.txt") as f:
        for line in f:
            items = line.strip().split("\t")
            author_id, author_info = items[0], items[1]
            sub_items = author_info.split("|")
            author_name, affi = sub_items[0], sub_items[1]

            author_id = "No." + str(author_id) + ""
            affi_id = "No." + str(affi_map[affi]) + ""

            au = URIRef(aca_au[author_id])
            af = URIRef(aca_af[affi_id])

            if (au, RDF.type, FOAF.Author) not in g:
                g.add((au, RDF.type, FOAF.Author))
                g.add((au, FOAF.name, Literal(author_name)))
            if (af, RDF.type, FOAF.Affiliation) not in g:
                g.add((af, RDF.type, FOAF.Affiliation))
                g.add((af, FOAF.name, Literal(affi)))

            g.add((au, FOAF.workIn, af))

        g.serialize(destination="author_graph.rdf", format="n3")
