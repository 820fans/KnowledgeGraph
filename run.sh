#!/usr/bin/env bash
# 清洗全国报刊索引的数据
# python wash_json_one_affi.py < paper_all.txt > paper_one_affi.txt

# 将每个人,按照姓名和机构 区分
python get_co_author.py < paper_one_affi.txt > co_author.txt
sort -u co_author.txt |awk '{printf("%d\t%s\n", NR,$0)}' > co_author_set.txt

# 提取机构, 并编号
awk -F "|" '{print $2}' co_author.txt| sort -u |awk '{printf("%d\t%s\n", NR, $0)}' > affiliation_set.txt

python create_graph.py