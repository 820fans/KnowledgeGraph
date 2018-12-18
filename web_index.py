# -*- coding: UTF-8 -*-


from flask import Flask, render_template, redirect, request
from rdflib import Graph

app = Flask(__name__)
g = Graph()
g.parse("au_af_graph.rdf", format="n3")

@app.route('/')
def hello_world():
    return "Hello Word!"

@app.route('/query/affi/<affi_id>')
def query(affi_id):
    qres = g.query(
            """   
            Prefix relation: <http://xmlns.com/foaf/0.1/>
            Prefix affi: <http://yida.academic.org/affiliation/>
            SELECT ?author_name WHERE { 
            ?author relation:workIn affi:No.12457 .
            ?author relation:name ?author_name
            }
            """)
    authors = []
    for row in qres:
        authors.append(row[0])

    # 渲染到模板
    return render_template("query_authors.html", authors=authors)


if __name__ == "__main__":
    app.run()