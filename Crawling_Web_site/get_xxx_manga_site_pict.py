#!/usr/bin/python3

# coding: UTF-8

##############################
## Module Import Seccrtion
##############################

import os # Directory作成などのため
import sys # モジュール属性 argv を取得するため
from datetime import datetime # 時間取得

sys.path.append('./libraries')


import urllib
## import urllib2
import requests


import zipfile
import shutil


import json
import collections as cl
import boto3

from bs4 import BeautifulSoup

##############################
## Var Setting Seccrtion
##############################

s3_bucket_name = "moka-comics"

argvs = sys.argv  # コマンドライン引数を格納したリストの取得
argc = len(argvs) # 引数の個数
# デバッグプリント
## print argvs
## print argc

if (argc != 4):   # 引数が足りない場合は、その旨を表示
    print ('Usage: # python %s [Start_page_num] [End_page_num] [Contents_code]' % argvs[0] ) 
    print ('Contents_Code: [001] = Ero_Dojin_Online, [002] = Ero_Managa_Log, [003] = Zetsubou_Manga_kan')
    quit()         # プログラムの終了


## Contents_code を変数に入れておく
c_code = argvs[3] 


if argvs[3] == '001':
    # アクセスするURL
    base_url = "http://eromangadoujinonline.com/category/%e3%82%aa%e3%83%aa%e3%82%b8%e3%83%8a%e3%83%ab"
    ## 作業ディレクトリの設定
    _list_json_file_ = "ero_dojin_online_list.json"
    _content_name_ = "Ero_Doujin_Online"
    f_prefix = "edol-"
elif argvs[3] == '002':
    # アクセスするURL
    base_url = "http://erodoujinlog.com/category/%e3%82%aa%e3%83%aa%e3%82%b8%e3%83%8a%e3%83%ab"
    ## 作業ディレクトリの設定
    _list_json_file_ = "ero_dojin_log_list.json"
    _content_name_ = "Ero_Doujin_Log"
    f_prefix = ""
elif argvs[3] == '003':
    # アクセスするURL
    base_url = "http://xn--gmq92kd2rm1kx34a.com/category/line-a/%e3%82%aa%e3%83%aa%e3%82%b8%e3%83%8a%e3%83%ab"
    ## 作業ディレクトリの設定
    _list_json_file_ = "zetsubou_manga_kan_list.json"
    _content_name_ = "Zetsubou_Manga_Kan"
    f_prefix = ""
else:
    print ('Contents_Code: [001] = Ero_Dojin_Online, [002] = Ero_Managa_Log, [003] = Zetsubou_Manga_kan')
    sys.exit(argvs[3] + ' is not registered Contents code')

print ( base_url,
        _list_json_file_,
        _content_name_)

####  ## 取得するサイト依存の情報
####  ## _content_name_ = "Ero_Doujin_Online"
####  _list_json_file_ = "ero_dojin_online_list.json"
####  ## _list_json_file_2_ = "sample_ero_dojin_online_list_NEW.json"
####  # アクセスするURL
####  base_url = "http://eromangadoujinonline.com/category/%e3%82%aa%e3%83%aa%e3%82%b8%e3%83%8a%e3%83%ab"


## 作業ディレクトリの設定
_tmp_dir_ = "tmp_list"


## 現在の日付・時間の取得設定
n_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
_n_date_ = datetime.now().strftime('%Y%m%d')


## 保存場所の設定
_s3_bucket_prefix_ = "XXXX-Comics/" + _content_name_ 

return_code = "\n"
source_url = ""

##############################
## Functions Setting Seccrtion
##############################


## JSON ファイルを読み込む 
def open_json_list_file_2():
    

    ## if os.path.exists("_list_json_file_"):
    json_f = open(_list_json_file_, 'r' )
    return json.load(json_f)
    json_f.close()
    ## else:
    ##     return ""

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

## 対象コンテンツのカテゴリ・非カテゴリページ一覧から一覧で表示されたコンテンツのURLを取得するための関数
def get_contents_url(html):

    ## html = get_html()

    # htmlをBeautifulSoupで扱う
    soup = BeautifulSoup(html, 'lxml')

    # タイトル要素を取得する 
    ### entrys_tag = soup.find_all("div", attrs={"class": "article-body-inner"})
    if c_code == '001': 
        entries_tag = soup.find_all("div", attrs={"class": "article-body-inner"})
    elif c_code == '002': 
        entries_tag = soup.find_all("h2", attrs={"class": "article-title entry-title"})
    elif c_code == '003':
        entries_tag = soup.find_all("div", attrs={"class": "post-header"})

    ### URLのみの抽出
    target_url_ary = []
    for entry in entries_tag:
        ## コンテンツ毎のスクレイピングrule
        if c_code == '001':
            entry_list = entry.find("a")
            target_cont = entry_list.attrs['href'],entry_list.attrs['title'] 
            target_url = entry_list.attrs['href'] 
        elif c_code == '002':
            entry_list = entry.find("a")
            target_cont = entry_list.attrs['href'],entry_list.attrs['title']
            target_url = entry_list.attrs['href']
        elif c_code == '003':
            entry_list = entry.find("h2").a
            target_cont = entry_list.attrs['href'],entry_list.text 
            target_url = entry_list.attrs['href']

        target_url_ary.append(target_url) 

    return target_url_ary

        ### target_url_ary.append(entry_list.attrs['href'])

        ### file.write(target_url)
        ### file.write(return_code)



## 各ページから画像をDownloadするためのURL取得するための関数:(エロ漫画同人オンライン)
def make_download_list(url_list):

    global pict_url_ary 
    pict_url_ary = [] 
    global cont_discriptions
    cont_discriptions = []

    ## コンテンツの名前やらファイル名の取得
    tmp_cont_number_01 = url_list.rsplit("/",1)
    cont_number = tmp_cont_number_01[1].split(".")
    archive_num = cont_number[0]
	
    req2 = request_as_fox(url_list)
    target_cont_html = urllib.request.urlopen(req2)
    ## 個別のページをパースする
    soup_2 = BeautifulSoup(target_cont_html, "html.parser") 


    ## メイン画像一覧のセクションの取得
    ## コンテンツ毎のスクレイピングrule
    if c_code == '001': 
        cont_entries_title = soup_2.find("title").text
        cont_entries_tag_1 = soup_2.find("section", attrs={"class": "entry-content"})  
        cont_entries_tag_2 = cont_entries_tag_1.find_all("img") 
        cont_discriptions = [ f_prefix + archive_num, cont_entries_title ]
    elif c_code == '002':  
        cont_entries_tag_1 = soup_2.find("section", attrs={"class": "entry-content"}) 
        cont_entries_title = cont_entries_tag_1.find("h3")
        cont_entries_tag_2 = cont_entries_tag_1.find_all("a")
        cont_discriptions = [ archive_num, cont_entries_title.text ]
    elif c_code == '003':
        cont_entries_title = soup_2.find("title").text
        cont_entries_tag_1 = soup_2.find("div", attrs={"class": "post-content"}) 
        cont_entries_id = cont_entries_tag_1.find("span").get("id")
        cont_entries_tag_2 = cont_entries_tag_1.find_all("img") 
        cont_discriptions = [ cont_entries_id, cont_entries_title ]

    for cet_ary in cont_entries_tag_2:
        if c_code in ['001', '003']: 
            pict_url_ary.append(cet_ary.attrs['src']) 
        elif c_code in ['002']: 
            pict_url_ary.append(cet_ary.attrs['href']) 


def dl_and_archive_files():

    ## 作業用のディレクトリの作成 
    tmp_files_dir = archive_name
    compress_file_name = archive_name + ".zip"
    s3_upload_name = _s3_bucket_prefix_  + "/" + _n_date_ + "/" + archive_name + ".zip"
    ## Download 作業用のディレクトリの作成
    if not os.path.exists(tmp_files_dir):
        os.mkdir(tmp_files_dir) 
        ## print ("create dl tamp dir")

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
    upload_file_to_s3(compress_file_name, s3_upload_name)

    ## アップロード後のZIPファイルの削除
    if os.path.exists(compress_file_name):
        os.remove(compress_file_name)


## S3 へのアップロード
def upload_file_to_s3(upload_target_name, s3_upload_path):
    s3 = boto3.resource('s3')
    s3_bucket = s3.Bucket(s3_bucket_name)
    s3_bucket.upload_file(upload_target_name, s3_upload_path)
	
## S3 からのダウンロード
def download_file_from_s3( _s3_key_, _local_path_ ):
    s3 = boto3.resource('s3')
    s3_bucket = s3.Bucket(s3_bucket_name)
    s3_bucket.download_file( _s3_key_, _local_path_ )
 	

## s3 内でのKeyの存在確認
def s3_key_exists(bucket: str, key: str) -> bool:
    s3 = boto3.client('s3')
    """
    指定した key が指定した bucket の中に存在するか

    :param bucket: (str) bucket name
    :param key: (str) key
    :return: (bool)
    """
    key_lists = s3.list_objects(Prefix=key, Bucket=bucket).get("Contents")
    if key_lists:
        for key_list in key_lists:
            if key_list.get("Key") == key:
                return True
    return False

def write_json_tmp_file():
    _json_dict_2_ = open_json_list_file_2() # JSONファイルを開いてみるDEBUG 2
    info_list.update(_json_dict_2_)
    ## print (info_list) #dict 形式での表示
    ## JSON 形式での書き出し
    print ('{}'.format(json.dumps(info_list,ensure_ascii=False,indent=4)))
    list_file = open( _list_json_file_, 'w')  #追加書き込みモードでオープン
    ## ファイルに書き出す
    json.dump(info_list,list_file,indent=4,ensure_ascii=False)
    list_file.close() ## デバッグ時暫定のlist_file用ファイルクローズ




############################################
## Main function
############################################

def main():
    ## ディレクトリ設定
    print(os.getcwd())

    ## 作業ディレクトリが存在しない場合は作成する
    if not os.path.exists(_tmp_dir_):
	    os.mkdir(_tmp_dir_)


    list_01 = []

    ### 各ページのURL 収集 実行セクション

    for i in range(int(argvs[1]),int(argvs[2])):
        source_url = base_url + "/page/" + str(i)
        html = get_html(source_url)
        ## return get_contents_url(html)
        list_01.extend(get_contents_url(html))
    ## print (list_01)
       
    print (""" ################################################# """)


    ## JSON 書き出し用のdict初期化
    info_list = cl.OrderedDict()

    ## 作業ディレクトリを変更する	
    os.chdir (_tmp_dir_)
    
    ##s3 上のJSONファイルの存在確認
    if s3_key_exists(s3_bucket_name, _s3_bucket_prefix_ + '/' + _list_json_file_):
        ### print ('JSONふぁいるはあるみたいよ')
        ## s3 からDL済みのJSONファイルをDLする
        s3_json_file = _s3_bucket_prefix_ + "/" + _list_json_file_ 
        download_file_from_s3(s3_json_file, _list_json_file_)
    else:
        ### print ('JSONふぁいるはないんだって・・・')
        ## 新しく空のJSONファイルを作成する
        new_json = open(_list_json_file_,'w')
        new_json.write('{}')
        new_json.close()

    num_of_list = 1
    for target_cont_url in list_01:

        ## 画像のURL一覧表示/コンテンツタイトル表示のための変数の宣言

        make_download_list(target_cont_url)
	
        global archive_name
        archive_name = cont_discriptions[0]
        print ("## -------- " +  cont_discriptions[0] + " (" + str(num_of_list) + "/" + str(len(list_01)) + ") " + " --------- ##")
        _json_dict_2_ = open_json_list_file_2() # JSONファイルを開いてみるDEBUG 2
        _json_dict_3_ = open_json_list_file_3(_json_dict_2_) # JSONファイルを開いてみるDEBUG 2

   
        ## JSONファイルのDL済みのURLリストと突き合わせ
        if cont_discriptions[0] in _json_dict_3_:
            print ('This ID Already Downloaded')
            num_of_list += 1
            continue
        else:
            print ('Download this file')

        print (cont_discriptions[1])
        info_list[cont_discriptions[0]] = cl.OrderedDict({'url':target_cont_url, 'Discription':cont_discriptions[1], 'Date':_n_date_ })

        ## 画像のURL一覧表示
        ## print (pict_url_ary[:]) # for DEBUG


#############################################

        dl_and_archive_files()

        num_of_list += 1

    
    ## ダウンロードしたコンテンツをJSON形式で表示する
    print ('{}'.format(json.dumps(info_list,ensure_ascii=False,indent=4)))

    ## JSON>>dictと今回DLしたファイルのdictを合体させる
    info_list.update(_json_dict_2_)

    ## print (info_list) #dict 形式での表示
    ## JSON 形式での書き出し
    ## print ('{}'.format(json.dumps(info_list,ensure_ascii=False,indent=4)))
    list_file = open( _list_json_file_, 'w')  #追加書き込みモードでオープン

    ## ファイルに書き出す
    json.dump(info_list,list_file,indent=4,ensure_ascii=False)
    list_file.close() ## デバッグ時暫定のlist_file用ファイルクローズ

    ## s3 にダウンロード済みリストJSONをアップロードする
    upload_file_to_s3(_list_json_file_, _s3_bucket_prefix_ + "/" + _list_json_file_ )


main()




