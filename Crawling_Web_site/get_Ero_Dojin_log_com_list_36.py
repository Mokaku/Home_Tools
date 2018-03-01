#!/usr/bin/python3



### #!/usr/bin/python 
# coding: UTF-8

##############################
## Module Import Seccrtion
##############################

import os # Directory作成などのため
import sys # モジュール属性 argv を取得するため
from datetime import datetime # 時間取得


import urllib
## import urllib2
import requests


import zipfile
import shutil


import json
import boto3

from bs4 import BeautifulSoup

s3_bucket_name = "moka-comics"

argvs = sys.argv  # コマンドライン引数を格納したリストの取得
argc = len(argvs) # 引数の個数
# デバッグプリント
## print argvs
## print argc

if (argc != 2):   # 引数が足りない場合は、その旨を表示
    print ('Usage: # python %s [page_num]' % argvs[0] )
    quit()         # プログラムの終了


# アクセスするURL
base_url = "http://erodoujinlog.com/category/%e3%82%aa%e3%83%aa%e3%82%b8%e3%83%8a%e3%83%ab"

return_code = "\n"
n_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
_n_date_ = datetime.now().strftime('%Y%m%d')

_content_name_ = "ero_doujin_log"

_s3_bucket_prefix_ = "XXXX-Comics/" + _content_name_ + "/" + _n_date_ 

source_url = ""


def request_as_fox(url):
    headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0"}
    return urllib.request.Request(url,None,headers)

def get_html(source_url):
    req = request_as_fox(source_url)
    response = urllib.request.urlopen(req)
    return response.read().decode('utf-8')
    ## print (html)


def get_contents_url(html):

    ## html = get_html()

    # htmlをBeautifulSoupで扱う
    soup = BeautifulSoup(html, 'lxml')

    # タイトル要素を取得する 
    entrys_tag = soup.find_all("h2", attrs={"class": "article-title entry-title"})

    ### print (entrys_tag)
    ### URLのみの抽出
    ### target_url_ary = []
    for entry in entrys_tag:
        entry_list = entry.find("a")
        ## return entry_list.attrs['href'] 
        target_url = entry_list.attrs['href'] 
        print (target_url)

        ### target_url_ary.append(entry_list.attrs['href'])

        ### file.write(target_url)
        ### file.write(return_code)



### 各ページのURL 収集 実行セクション


target_url_ary = [] 
def get_all_url():

    for i in range(int(argvs[1])):
        source_url = base_url + "/page/" + str(i)
        print (source_url)
        html = get_html(source_url)
        target_url_ary.append(get_contents_url(html))




get_all_url()

print (target_url_ary[:])

'''

## USER-Agent 縛りの逃げ
opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib2.install_opener(opener)



def get_contents_url():
	html = urllib2.urlopen(url)

	# htmlをBeautifulSoupで扱う
	soup = BeautifulSoup(html, "html.parser")
	
	# タイトル要素を取得する → <title>経済、株価、ビジネス、政治のニュース:日経電子版</title>
	## title_tag = soup.title
	entrys_tag = soup.find_all("h2", attrs={"class": "article-title entry-title"})

	# 要素の文字列を取得する → 経済、株価、ビジネス、政治のニュース:日経電子版
	## title = title_tag.string

	##entry_string_url = ""
	# タイトル要素を出力

	for entry in entrys_tag:
##		print "#-----------------------------------#"
		entry_list = entry.find("a")
		## print entry_list.attrs['href'],entry_list.text
		## url_list_ary = entry_list.attrs['href'],entry_list.text 
		target_url = entry_list.attrs['href'] 
		target_url_ary.append(entry_list.attrs['href'])
		## file.writelines(entry_list.attrs['href']) 
		file.write(target_url)
		file.write(return_code)

	pass  

# タイトルを文字列を出力
## print title


print(os.getcwd())

tmp_dir = "tmp_list"
if not os.path.exists(tmp_dir):
	os.mkdir(tmp_dir)

tmp_file_name = tmp_dir + "/" + "test_ero_dojin_" + n_datetime + ".list"
file = open(tmp_file_name, 'a')  #追加書き込みモードでオープン

target_url_ary = []
 
for i in range(int(argvs[1])):
	url = base_url + "/page/" + str(i)
	print url
	get_contents_url()

file.close()

print target_url_ary[:]
print """
@#################################################
"""

def make_download_list():
	
	target_cont_html = urllib2.urlopen(target_cont_url)
	## 個別のページをパースする
	soup_2 = BeautifulSoup(target_cont_html, "html.parser") 

	## メイン画像一覧のセクションの取得
	cont_entris_tag_1 = soup_2.find("section", attrs={"class": "entry-content"})
	## debug
	## print cont_entris_tag_1
	## print "## -------------------- ##"

	## cont_entris_tag_2 = cont_entris_tag_1.find_all("a")
	cont_entris_title = cont_entris_tag_1.find("h3")
	cont_entris_tag_2 = cont_entris_tag_1.find_all("a")

	print "## -------------------- ##"
	global cont_discriptions
	cont_discriptions = cont_entris_title.text

	for cet_ary in cont_entris_tag_2:
	##	print cet_ary.attrs['href']
		pict_url_ary.append(cet_ary.attrs['href'])
	##	print url_2
	
##	for entry_main in cont_entris_tag_2:
##		print "#-----------------------------------#"
##		entry_list_main = entry_main.find_all("a")
##		print entry_list_main


	pass


for target_cont_url in target_url_ary:
	## コンテンツの名前やらファイル名の取得
	tmp_cont_number_01 = target_cont_url.rsplit("/",1)
	cont_number = tmp_cont_number_01[1].split(".")
	archive_name = cont_number[0]


	## print target_cont_url
	print archive_name


	
	## 画像のURL一覧表示/コンテンツタイトル表示のための変数の宣言
	pict_url_ary = [] 
	### cont_entris_title = []
	cont_discriptions = []

	make_download_list()
	
	print cont_discriptions
	print "## -------------------- ##"

	## 画像のURL一覧表示
	### print pict_url_ary[:] # for DEBUG


	tmp_files_dir = tmp_dir + "/" + archive_name
	compress_file_name = tmp_dir + "/" + archive_name + ".zip"
	s3_upload_name = _s3_bucket_prefix_  + "/" +archive_name + ".zip"
	## Download 作業用のディレクトリの作成
	if not os.path.exists(tmp_files_dir):
		os.mkdir(tmp_files_dir) 


	## ZIP書庫の作成
	print compress_file_name
	compFile = zipfile.ZipFile(compress_file_name, 'w', zipfile.ZIP_STORED)

	##実ファイルのダウンロード

	for dl_file in pict_url_ary:
		file_url = dl_file
		savename_ary = dl_file.rsplit("/",1)
		savename = tmp_files_dir + "/" +savename_ary[1]
		readme_file = tmp_files_dir + "/00_README.md"
		
		print file_url,savename,tmp_files_dir

		## Discription File の作成
		## if not os.path.exists(readme_file):
		##	r_file = open(readme_file, 'w')  #追加書き込みモードでオープン
		##
		##	r_file.write(cont_discriptions)
		##	r_file.close() 
		
		
		## urllib.request.urlretrieve(file_url, savename)
		## urllib.urlretrieve(file_url, savename)

		req = requests.get(file_url)
		if req.status_code == 200:
			## ファイル保存
			f = open(savename, 'wb')
			f.write(req.content)
			f.close()
			

		
	## DLしたファイルを書庫に追加
	compFile.write(savename)

		
	
	## ZIP 書庫をクローズ
	compFile.close()

		
	## 作業用のディレクトリの削除
	if os.path.exists(tmp_files_dir):
		shutil.rmtree(tmp_files_dir)

	## S3 へのアップロード

	s3 = boto3.resource('s3')
	s3_bucket = s3.Bucket(s3_bucket_name)
	s3_bucket.upload_file(compress_file_name, s3_upload_name)
	
	## アップロード後のZIPファイルの削除
	if os.path.exists(compress_file_name):
		os.remove(compress_file_name)

		

	print """ ## ------------------------------------------- ##

	
	
	"""

'''
