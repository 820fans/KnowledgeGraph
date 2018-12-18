# -*- coding: UTF-8 -*-

import re

id_pattern = re.compile("#index([^\r\n]*)")
title_pattern = re.compile("#\*([^\r\n]*)")
author_pattern = re.compile("#@([^\r\n]*)")
affiliations_pattern = re.compile("#o([^\r\n]*)")
year_pattern = re.compile("#t ([0-9]*)")
journal_pattern = re.compile("#c([^\r\n]*)")
refs_pattern = re.compile("#%([^\r\n]*)")
abstract_pattern = re.compile("#!([^\r\n]*)")

name_pattern = re.compile("#n([^\r\n]*)")
affiliation_pattern = re.compile("#a([^\r\n]*)")
pc_pattern = re.compile("#pc([^\r\n]*)")
cn_pattern = re.compile("#cn([^\r\n]*)")
hi_pattern = re.compile("#hi([^\r\n]*)")
pi_pattern = re.compile("#pi([^\r\n]*)")
upi_pattern = re.compile("#upi([^\r\n]*)")
t_pattern = re.compile("#t([^\r\n]*)")

import MySQLdb
conn = MySQLdb.connect(host= "localhost",
                  user="root",
                  passwd="root",
                  db="aminder")
x = conn.cursor()
import codecs
author_csv = codecs.open("data/authors.csv", "w")
paper_csv = codecs.open("data/papers.csv", "w")
cite_csv = codecs.open("data/citations.csv", "w")
coauthor_csv = codecs.open("data/coauthors.csv", "w")
author2paper_csv = codecs.open("data/author2paper.csv", "w")


def write_header():
    author_csv.write("{|}".join(['id', 'name', 'affiliation', 'pub_num', 'cite_num',
                               'h_index', 'p_index', 'up_index', 'interest']) + "\n")
    paper_csv.write("{|}".join(['id', 'title', 'abstract', 'authors', 'affiliations',
                              'year', 'journal', 'refs']) + "\n")
    cite_csv.write("{|}".join(['paper_id', 'cited_paper_id']) + "\n")
    coauthor_csv.write("{|}".join(['author_id_a', 'author_id_b', 'co_num']) + "\n")
    author2paper_csv.write("{|}".join(['author_id', 'paper_id', 'position']) + "\n")

write_header()


class Paper:
    __slots__ = ['id', 'title', 'authors', 'affiliations', 'refs', 'year', 'journal', 'abstract']
    csv_header = ('id', 'title', 'abstract', 'authors', 'affiliations', 'year', 'journal', 'refs')

    def __init__(self, id):
        self.id = int(id)
        self.title = ""
        self.authors = []
        self.affiliations = []
        self.abstract = ""
        self.year = 0
        self.journal = ""
        self.refs = []

    def get_or_none(self, attr):
        try:
            val = getattr(self, attr)
            if isinstance(val, list):
                val = ";".join(val)
            return str(val)
        except:
            return ""

    def csv_attrs(self):
        attrs = [self.get_or_none(attr) for attr in self.csv_header]
        paper_csv.write("{|}".join(attrs) + "\n")

        for ref in self.refs:
            cite_csv.write("{|}".join([str(self.id), str(ref)]) + "\n")
        # sql = "INSERT INTO `paper` (`id`, `title`, `abstract`, `authors`, `affiliations`, `year`, `journal`, `refs`) VALUES (%d, '%s', '%s', '%s', '%s', %d, '%s', '%s');" \
        #       % (attrs[0], attrs[1], attrs[2], attrs[3], attrs[4], attrs[5], attrs[6], attrs[7])
        #
        # x.execute(sql)
        # conn.commit()
        # return sql

class Author:
    __slots__ = ['id', 'name', 'affiliation', 'pub_num', 'cite_num', 'h_index', 'p_index', 'up_index', 'interest']
    csv_header = ('id', 'name', 'affiliation', 'pub_num', 'cite_num', 'h_index', 'p_index', 'up_index', 'interest')

    def __init__(self, id):
        self.id = int(id)
        self.header_index = [attr for attr in self.csv_header]

    def get_or_none(self, attr):
        try:
            val = getattr(self, attr)
            if isinstance(val, list):
                val = ";".join(val)
            return str(val)
        except:
            return ""

    def csv_attrs(self):
        attrs = [self.get_or_none(attr) for attr in self.csv_header]
        author_csv.write("{|}".join(attrs) + "\n")
        # return df
        # sql = "INSERT INTO `author` (`id`, `name`, `affiliation`, `pub_num`, `cite_num`, `h_index`, `p_index`, `up_index`, `interest`) VALUES (%d, '%s', '%s', %d, %d, %d, %f, %f, '%s');" \
        #       % (attrs[0], attrs[1], attrs[2], attrs[3], attrs[4], attrs[5], attrs[6], attrs[7], attrs[8])
        #
        # x.execute(sql)
        # conn.commit()

class Author2Paper:
    id = 0
    author_id = 0
    paper_id = 0
    position = 0

class Washer:

    @staticmethod
    def safeInt(val):
        try:
            ye = int(val)
            return ye
        except:
            return 0
    @staticmethod
    def safeFloat(val):
        try:
            return float(val)
        except:
            return 0.0

    def match(self, line, pattern):
        """Return first group of match on line for pattern."""
        m = pattern.match(line)
        return m.groups()[0].strip() if m else None

    def wash_paper(self, fname):
        with open(fname) as f:
            line = f.readline()
            while len(line.strip()) > 0:
                id = self.match(line, id_pattern)
                data_lines = []
                if id is not None:
                    while True:
                        line = f.readline()
                        if len(line.strip()) == 0:
                            break
                        else:
                            data_lines.append(line)
                i = 0
                paper = Paper(id)
                while i < len(data_lines):
                    line = data_lines[i]
                    if line.startswith("#*"):
                        paper.title = self.match(line, title_pattern).replace('"', '\'')
                    elif line.startswith("#@"):
                        authors = self.match(line, author_pattern).replace('"', '\'')
                        paper.authors = authors.split(";")
                    elif line.startswith("#o"):
                        affiliations = self.match(line, affiliations_pattern).replace('"', '\'')
                        paper.affiliations = affiliations.split(";")
                    elif line.startswith("#t"):
                        year = self.match(line, year_pattern)
                        paper.year = self.safeInt(year)
                    elif line.startswith("#c"):
                        journal = self.match(line, journal_pattern).replace('"', '\'')
                        paper.journal = journal
                    elif line.startswith("#%"):
                        ref_id = self.match(line, refs_pattern)
                        paper.refs.append(ref_id)
                    elif line.startswith("#!"):
                        abstract = self.match(line, abstract_pattern).replace('"', '\'')
                        paper.abstract = abstract
                    i += 1
                # print paper.refs
                paper.csv_attrs()
                line = f.readline()

    def wash_author(self, fname):
        with open(fname) as f:
            line = f.readline()
            while len(line.strip()) > 0:
                id = self.match(line, id_pattern)
                data_lines = []
                if id is not None:
                    while True:
                        line = f.readline()
                        if len(line.strip()) == 0:
                            break
                        else:
                            data_lines.append(line)
                i = 0
                author = Author(id)
                while i < len(data_lines):
                    line = data_lines[i]
                    if line.startswith("#n"):
                        author.name = self.match(line, name_pattern)
                    elif line.startswith("#a"):
                        author.affiliation = self.match(line, affiliation_pattern)
                    elif line.startswith("#pc"):
                        author.pub_num = Washer.safeInt(self.match(line, pc_pattern))
                    elif line.startswith("#cn"):
                        author.cite_num = Washer.safeInt(self.match(line, cn_pattern))
                    elif line.startswith("#hi"):
                        author.h_index = Washer.safeInt(self.match(line, hi_pattern))
                    elif line.startswith("#pi"):
                        author.p_index = Washer.safeFloat(self.match(line, pi_pattern))
                    elif line.startswith("#upi"):
                        author.up_index = Washer.safeFloat(self.match(line, upi_pattern))
                    elif line.startswith("#t"):
                        author.interest = self.match(line, t_pattern)
                    i += 1

                author.csv_attrs()
                line = f.readline()

    def wash_author2paper(self, fname):
        with open(fname) as f:
            for line in f:
                line = line.strip()
                if len(line) == 0: continue
                items = line.split(",")
                author2paper_csv.write("{|}".join([items[0], items[1],items[2]]) + "\n")
                # sql ="INSERT INTO `author2paper` (`author_id`, `paper_id`, `position`) VALUES ( '%s', '%s', '%s')" \
                #       % (items[0], items[1],items[2])
                # x.execute(sql)
                # conn.commit()

    def wash_coauthor(self, fname):
        with open(fname) as f:
            for line in f:
                line = line.strip()
                if len(line) == 0: continue
                items = line.split("\t")
                coauthor_csv.write("{|}".join([items[0].replace("#", ""), items[1], items[2]]) + "\n")
                # sql = "INSERT INTO `coauthor` (`author_id_a`, `author_id_b`, `co_num`) VALUES('%s', '%s', '%s');" \
                #        % (items[0].replace("#", ""), items[1], items[2])
                # x.execute(sql)
                # conn.commit()




if __name__ == "__main__":
    Washer().wash_paper("./Paper.txt")
    Washer().wash_author("./Author.txt")
    # Washer().wash_author("./author-t100.txt")
    # Washer().wash_paper("./paper-t100.txt")
    Washer().wash_author2paper("./author2paper.csv")
    Washer().wash_coauthor("./Coauthor.txt")