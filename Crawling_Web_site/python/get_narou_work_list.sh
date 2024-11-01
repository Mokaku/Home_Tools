#!/bin/bash

list_dir="../../novel_database/"
list_file="narou_all_novel_id.list"

cat ${list_dir}${list_file} |\
	while read line;
		do \
			  ncode_id=$(echo ${line} | cut -d , -f 1)
			  ncode_get_flg=$(echo ${line} | cut -d , -f 2)
			  ncode_ref=$(echo ${line} | cut -d , -f 3)
			# echo $line
			# echo ${ncode_id}
			# echo ${ncode_ref}
			# echo "GET_FLAG: ${ncode_get_flg}"
			if [ ${ncode_get_flg} == 1 ]; then
				python get_narou_TableOfContents.py ${ncode_id};
			else
				echo "PASS: ${ncode_ref}"
			fi
			
		done