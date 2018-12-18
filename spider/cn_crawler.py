import codecs
import json
import optparse
import os
import random
import sys
import time
from pprint import pprint
from threading import Thread

import requests

session = requests.session()


def special_search(
        sentence,
        save_path,
        page_args,
        doc_args,
        debug=False,
):
    """
    Search the documents in cnbksy.com
    :param sentence:
    :param save_path:
    :param page_args: A list of [start_page(record current page), end_page]
    :param doc_args:  A list of [documents count, total document]
    :param debug:
    :return:
    """
    if os.path.isfile(save_path):
        os.remove(save_path)
    session.get("http://www.cnbksy.com/search/special")
    csrf = session.cookies.get("XSRF-TOKEN")
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0",
        "Content-Type": "application/json",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Connection": "keep-alive"
    }
    while page_args[1] is None or page_args[0] <= page_args[1]:
        # time.sleep(random.randint(2, 7))
        # current_page_backup = page_args[0]
        try:
            post_param = {
                "products": ["P_325", "P_324", "P_162", "P_163", "P_102", "P_103", "P_83",
                             "P_84", "P_78", "P_77", "P_76", "P_75", "P_74",
                             "P_73", "P_183", "P_182", "P_104", "P_105",
                             "P_85", "P_86", "P_72", "P_71", "P_70", "P_69",
                             "P_68", "P_67", "P_66", "P_65", "P_64", "P_63", "P_62"],
                "isSelectedAll": True,
                "query": sentence,
                "currentPage": page_args[0],
                "lastquery": "",
                "lastPrettyQuery": "", "isRestart": True,
                "pageCount": "50", "asc": "false", "relative": "true", "typeId": 1, "facets": []}
            page = session.post("http://www.cnbksy.com/search/specialQuery?_csrf={}"
                                .format(csrf), headers=headers, json=post_param)
            page_json = page.json()
            result = page_json[0]
            if result is None:
                print("No result is found!")
                return 2
            page_args[1] = result.get('pageCount')
            documents = result.get('documents')
            if documents is None:
                print("No document is found!")
                return 3
            for document in documents:
                data = {
                    "Title": document.get("Title1Cn"),
                    "Authors": document.get("AU_F"),
                    "AuthorsAffiliations": document.get("AF"),
                    "Subjects": document.get("Subjects"),
                    "Abstract": document.get("Abstract"),
                    "Year": document.get("Year"),
                    "Literature": document.get("LiteratureTitle"),
                    "CLC": document.get("CLC")
                }
                # if debug:
                #     pprint(data)
                for key in data:
                    if not data.get(key):
                        break
                else:
                    with codecs.open(save_path, "a", "UTF-8") as f:
                        json.dump(data, f, ensure_ascii=False)
                        f.write("\n")
                    doc_args[0] += 1
                    if doc_args[0] == doc_args[1]:
                        print("End of {}".format(sentence))
                        return 0
            page_args[0] += 1
        except Exception as e:
            session.get("http://www.cnbksy.com/search/special")
            csrf = session.cookies.get(   "XSRF-TOKEN")
            if debug:
                print(e)
    print("End of {}".format(sentence))
    return 0


def get_documents():
    doc_args_dict = {
        "TP31": ("CLC:TP31*", [0, None], [0, 10000]),
    }
    for key in doc_args_dict:
        thread = Thread(target=special_search, args=(
            doc_args_dict[key][0],
            "data_{}.dat".format(key),
            doc_args_dict[key][1],
            doc_args_dict[key][2]
        ))
        thread.start()

    def show_progress():
        while True:
            for dict_key in doc_args_dict:
                print("{}|pages|{}/{}|documents|{}/{}||".format(
                    dict_key,
                    doc_args_dict[dict_key][1][0],
                    doc_args_dict[dict_key][1][1],
                    doc_args_dict[dict_key][2][0],
                    doc_args_dict[dict_key][2][1]
                ), end="\t")
            print()
            time.sleep(10)
    Thread(target=show_progress, daemon=True).start()


def main():
    usage = """
    cn_crawler.py [option] <query string>
    e.g. python cn_crawler.py -o TP -d -s 1 "CLC:TP*"
    """
    fmt = optparse.IndentedHelpFormatter(max_help_position=50, width=100)
    parser = optparse.OptionParser(usage=usage, formatter=fmt)
    group = optparse.OptionGroup(parser, "Query arguments",
                                 "These options define search query arguments and parameters.")
    group.add_option("-o", "--output", default="Result")
    group.add_option("-d", "--debug", action="count", default=0)
    group.add_option("-s", "--start_page", type="int", default=1)
    group.add_option("-t", "--thread_count", type="int", default=5)
    parser.add_option_group(group)
    options, _ = parser.parse_args()

    if len(sys.argv) < 1:
        parser.print_help()
        return 1

    start_page = options.start_page
    return 0


if __name__ == "__main__":
    sys.exit(get_documents())
