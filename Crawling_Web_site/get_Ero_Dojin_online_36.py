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
import collections as cl
import boto3

from bs4 import BeautifulSoup

s3_bucket_name = "moka-comics"

argvs = sys.argv  # コマンドライン引数を格納したリストの取得
argc = len(argvs) # 引数の個数
# デバッグプリント
## print argvs
## print argc

if (argc != 3):   # 引数が足りない場合は、その旨を表示
    print ('Usage: # python %s [Start_page_num] [End_page_num]' % argvs[0] )
    quit()         # プログラムの終了


# アクセスするURL
base_url = "http://eromangadoujinonline.com/category/%e3%82%aa%e3%83%aa%e3%82%b8%e3%83%8a%e3%83%ab"
## 作業ディレクトリの設定
_tmp_dir_ = "tmp_list"
_list_json_file_ = "sample_ero_dojin_online_list.json"
_list_json_file_2_ = "sample_ero_dojin_online_list_NEW.json"


return_code = "\n"

## 現在の日付・時間の取得設定
n_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
_n_date_ = datetime.now().strftime('%Y%m%d')

_content_name_ = "Ero_Doujin_Online"

_s3_bucket_prefix_ = "XXXX-Comics/" + _content_name_ + "/" + _n_date_ 

source_url = ""


## JSON ファイルを読み込む
## def open_json_list_file():
## 
##     json_f = open(_list_json_file_, 'r' )
##     json_data = json.load(json_f)
##     global json_content_id
##     json_content_id = []
## 
##     for x in json_data:
##         json_content_id.append('{0}'.format(x,json_data[x]))

## JSON ファイルを読み込む 2
def open_json_list_file_2():

    json_f = open(_list_json_file_, 'r' )
    return json.load(json_f)
    json_f.close()

## JSON から抽出したdictから必要なIDを抜き出してlistにする
def open_json_list_file_3(dict_all):
    
    ## return dict_all

    global json_content_id_2
    json_content_id_2 = []
    for x in dict_all:
        json_content_id_2.append('{0}'.format(x,dict_all[x]))
    return json_content_id_2


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
    entrys_tag = soup.find_all("div", attrs={"class": "article-body-inner"})

    ## print (entrys_tag)
    ### URLのみの抽出
    ### target_url_ary = []
    for entry in entrys_tag:
        entry_list = entry.find("a")
        ## return entry_list.attrs['href'] 
        target_cont = entry_list.attrs['href'],entry_list.attrs['title']
        target_url = entry_list.attrs['href']
        ## print (entry_list)
        ## print (target_cont)
        target_url_ary.append(target_url)

        ### target_url_ary.append(entry_list.attrs['href'])

        ### file.write(target_url)
        ### file.write(return_code)


## ディレクトリ設定

print(os.getcwd())

## 作業ディレクトリが存在しない場合は作成する
if not os.path.exists(_tmp_dir_):
	os.mkdir(_tmp_dir_)

tmp_file_name = _tmp_dir_ + "/" + "test_ero_dojin_online_" + n_datetime + ".list"
## list_file = open( _tmp_dir_ + "/" + _list_json_file_, 'w')  #追加書き込みモードでオープン


### 各ページのURL 収集 実行セクション


target_url_ary = [] 
## def get_all_url():

for i in range(int(argvs[1]),int(argvs[2])):
    source_url = base_url + "/page/" + str(i)
    ## print (source_url)
    html = get_html(source_url)
    get_contents_url(html)

## file.close() 



## get_all_url()

## print (target_url_ary[:])


print ("""
#################################################
""")

def make_download_list():


    ## コンテンツの名前やらファイル名の取得
    tmp_cont_number_01 = target_cont_url.rsplit("/",1)
    cont_number = tmp_cont_number_01[1].split(".")
    archive_num = cont_number[0]
	
    req2 = request_as_fox(target_cont_url)
    target_cont_html = urllib.request.urlopen(req2)
    ## 個別のページをパースする
    soup_2 = BeautifulSoup(target_cont_html, "html.parser") 

    ## メイン画像一覧のセクションの取得
    cont_entries_title = soup_2.find("title").text
    cont_entries_tag_1 = soup_2.find("section", attrs={"class": "entry-content"})
    ## Debug
    ## print (cont_entries_tag_1)
    ## print "## -------------------- ##"

    ## cont_entries_tag_2 = cont_entries_tag_1.find_all("a")
    ## cont_entries_id = cont_entries_tag_1.find("span")
    cont_entries_tag_2 = cont_entries_tag_1.find_all("img")

    global cont_discriptions
    cont_discriptions = [ "edol-" + archive_num, cont_entries_title ]

    for cet_ary in cont_entries_tag_2:
        ##	print cet_ary.attrs['href']
    	pict_url_ary.append(cet_ary.attrs['src'])
        ##	print url_2

## JSON 書き出し用のdict初期化
info_list = cl.OrderedDict()

## 作業ディレクトリを変更する	
os.chdir (_tmp_dir_)

for target_cont_url in target_url_ary:


    ## print target_cont_url
    ### print (archive_name)


	
    ## 画像のURL一覧表示/コンテンツタイトル表示のための変数の宣言
    pict_url_ary = [] 
    ### cont_entries_title = []
    cont_discriptions = []

    make_download_list()
	
    ## print (cont_entries_id)
    archive_name = cont_discriptions[0]
    print ("## -------- " +  cont_discriptions[0] + " --------- ##")
    ## open_json_list_file() # 保存したJSONファイルを開いてみるDEBUG
    _json_dict_2_ = open_json_list_file_2() # JSONファイルを開いてみるDEBUG 2
    _json_dict_3_ = open_json_list_file_3(_json_dict_2_) # JSONファイルを開いてみるDEBUG 2

    ## print (_json_dict_3_)
   
    ##### 一時的にこのブロックコメントアウト
    if cont_discriptions[0] in _json_dict_3_:
        print ('This ID Already Downloaded')
        continue
    else:
        print ('Download this file')

    ## print (cont_discriptions[0])
    print (cont_discriptions[1])
    info_list[cont_discriptions[0]] = cl.OrderedDict({'url':target_cont_url, 'Discription':cont_discriptions[1]})
    ##list_file.write(info_list[:])
    ## print ("## -------------------- ##")

    ## 画像のURL一覧表示
    ## print (pict_url_ary[:]) # for DEBUG





##########################################################################################

    ## 作業用のディレクトリの作成 
    tmp_files_dir = archive_name
    compress_file_name = archive_name + ".zip"
    s3_upload_name = _s3_bucket_prefix_  + "/" +archive_name + ".zip"
    ## Download 作業用のディレクトリの作成
    if not os.path.exists(tmp_files_dir):
        os.mkdir(tmp_files_dir) 
        print ("create dl tamp dir")


    ## ZIP書庫の作成
    print (compress_file_name)
    compFile = zipfile.ZipFile(compress_file_name, 'w', zipfile.ZIP_STORED)

    ##実ファイルのダウンロード

    for dl_file in pict_url_ary:
        file_url = dl_file
        savename_ary = dl_file.rsplit("/",1)
        savename = tmp_files_dir + "/" +savename_ary[1]
        readme_file = tmp_files_dir + "/00_README.md"
		
        print (file_url,savename,tmp_files_dir)

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

		

    print (""" ## ------------------------------------------- ##
	
    """)


_json_dict_2_ = open_json_list_file_2() # JSONファイルを開いてみるDEBUG 2
## print (info_list) #dict 形式での表示
## print ("## -------------------- ##")
info_list.update(_json_dict_2_)
## print (info_list) #dict 形式での表示
## JSON 形式での書き出し
print ('{}'.format(json.dumps(info_list,ensure_ascii=False,indent=4)))
list_file = open( _list_json_file_, 'w')  #追加書き込みモードでオープン
## ファイルに書き出す
json.dump(info_list,list_file,indent=4,ensure_ascii=False)
list_file.close() ## デバッグ時暫定のlist_file用ファイルクローズ


'''
##########################################################################################
'''

