#!/bin/bash

list_dir="../../novel_database/"
list_file="kakuyomu_all_novel_id.list"

cat ${list_dir}${list_file} |\
	while read line;
		# do \
		# 	python get_kakuyomu_TableOfContents.py $line;
		do \
			work_id=$(echo ${line} | cut -d , -f 1)
			work_get_flg=$(echo ${line} | cut -d , -f 2)
			work_ref=$(echo ${line} | cut -d , -f 3)
			# echo "LINE: ${line}"
			# echo "ID: ${work_id}"
			# echo "Reference: ${work_ref}"
			echo "### ${work_id}##################"
			echo "GET_FLAG: ${work_get_flg}"
			if [ ${work_get_flg} = 1 ]; then
				python get_kakuyomu_TableOfContents.py ${work_id};
				## python Debug_get_kakuyomu_TableOfContents_00.py ${work_id};
			else
				echo ""
				echo "### PASS: ${work_ref}"

			fi

		done
