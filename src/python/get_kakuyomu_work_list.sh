#!/bin/bash

list_dir="../../novel_database/"
list_file="all_novel_id.list"

cat ${list_dir}${list_file} |\
	while read line;
		do \
			python get_kakuyomu_TableOfContents.py $line;
		done