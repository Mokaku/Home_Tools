import requests
import json
import datetime
import sys
from bs4 import BeautifulSoup

args = sys.argv

print(args[1])
print(len(args))

if 2 <= len(args):
	novel_id = args[1]
	# if args[1].isdigit():
	# 	novel_id = args[1]
	# else:
	# 	print('Argument is not digit')
else:
	print('Arguments are too short')

source_dir="../../json_source"
source_file="daysneo_da59da23660b4fa346e5717aed10e147.html"

novel_url = "https://ncode.syosetu.com"
prefix = "narou_"

## なろうサイトではUAが存在していないとデータが取得できない(403で返る）ためにUAを設定
ua_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0"}

#########################
## なろう小説ID(for test)##
#########################
# novel_id = "n6453iq" # 春暁記
# novel_id = "n3289ds" # のんびり農家
# novel_id = "n1146do" # 捨て子になりましたが、魔法のおかげで大丈夫そうです
# novel_id = "2710db" #とんでもスキルで異世界放浪メシ
# novel_id = "n9636x" #薬屋のひとりごと



# https://ncode.syosetu.com/n6453iq/

load_url = novel_url + "/" + novel_id + "/"

# source_file_name = source_dir + "/" + source_file
html = requests.get(load_url , headers = ua_headers)
soup = BeautifulSoup(html.content, "html.parser")

# タイトルと説明を抽出してJSON形式に変換
json_data = []
id_counter = 1

# soup = BeautifulSoup(html, "html.parser")
# requests でソースを取得する場合は”．content”を付ける必要がある

json_filename = '../../html/narou/json/' + prefix + novel_id + '.json'
html_filename = '../../html/narou/' + prefix + novel_id + '.html'

###################################################
## bt4 module 使い方メモ
###################################################
# HTML全体を表示する
# print(soup)

# title、h2、liタグを検索して表示する
# print(soup.find("title").text)    # タグを検索して表示
# print(soup.find("h2"))
# print(soup.find("li"))
# print(soup.find(id="__NEXT_DATA__").text)
###################################################

def get_novel_base_info():
	novel_series = (soup.find(class_= "p-novel__series"))
	if novel_series == None:
		novel_series_name = "N/A"
	else:
		novel_series_name = novel_series.text.strip() # type: ignore
	# print (novel_series_name)
	novel_title = (soup.find(class_= "p-novel__title")).text.strip() # type: ignore
	# print (novel_title)
	novel_auther = (soup.find(class_= "p-novel__author")).text.strip() # type: ignore
	return ( [novel_series_name,novel_title,novel_auther] )


def get_page_counts():
	novel_page_contents = (soup.find("div" , class_= "c-pager"))
	last_page_line = (novel_page_contents.find("a", class_="c-pager__item c-pager__item--last")) # type: ignore
	last_page_url = last_page_line["href"]
	last_page_num = last_page_url.split('?')[1].split('=')[1]
	## debug ###
	# print("Section.--------------------------------")
	# print (novel_main_contents)
	# print("Line.--------------------------------")
	# print (last_page_line)
	# print("num.--------------------------------")
	# print (last_page_url)
	return (last_page_num)

def get_all_pages(page_num,novel_series_name, novel_title, novel_auther):
	ep_num=int(1)
	chp_num=int(1)
	page_num = int(page_num) + 1
	contents_json = {        "__typename": "Story","id": novel_id,"serieis": novel_series_name, "title": novel_title, "AutherName": novel_auther,}

	## Chapterの無いNovelのためにます、 ep_list とchapter_jsonを初期化しておく。
	chapter_json_name = "Chapters_1"
	ep_list = []
	chapter_json = { "__typename": "Chapter", "chp_num": "", "ChapterName": "", "Episode": ep_list } 

	for get_page_num in range(1, page_num):
		# print ("Page:",get_page_num,"#-----")
		_load_url = "{}/{}/?p={}".format(novel_url,novel_id,get_page_num)
		l_html = requests.get(_load_url , headers = ua_headers)
		l_soup = BeautifulSoup(l_html.content, "html.parser")
		novel_main_contents = (l_soup.find("div" , class_= "p-eplist"))
		# novel_ep_contents_list = (novel_main_contents.find("div" , class_= "p-eplist__subtitle"))
		novel_ep_contents_list = (novel_main_contents.find_all(class_=['p-eplist__chapter-title','p-eplist__sublist']))
		# print ("-----------------------")	
		# print (novel_ep_contents_list)	
		# novel_ep_contents_list = (novel_main_contents.select('a'))

		for key in novel_ep_contents_list:
			# print ("### -----------------------")	
			# print ("#1",key)
			# print ("------------")	
			if (key.find(class_="p-eplist__subtitle")) == None:
				key_cp_title = key.text.strip()
				chapter_json_name = '{}_{}'.format("Chapters",chp_num)
				## Chapterの存在するNovelの場合、章分割のために ep_list とchapter_jsonを再度初期化。
				ep_list = []
				chapter_json = { "__typename": "Chapter", "chp_num": chp_num, "ChapterName": key_cp_title, "Episode": ep_list } 
				# print('Chapter {} {}'.format(chp_num,key_cp_title))
				# print( chapter_json )
				chp_num = chp_num+1
			else:
				key_link = (key.find(class_="p-eplist__subtitle"))
				key_update_date = (key.find(class_="p-eplist__update"))
				# print ("#2",key_link," / ",key_update_date)	
				# print ("------------")	
				novel_sub_url = (novel_url + key_link.get("href"))
				novel_sub_title = key_link.text.strip()
				novel_sub_update = key_update_date.text.strip().replace("\n","")
				ep_list.append( {"__typename": "Episode","ep_num": ep_num, "url": novel_sub_url, "title": novel_sub_title, "publishedAt":novel_sub_update} ) 
				chapter_json["Episode"] = ep_list
				contents_json[chapter_json_name] = chapter_json
				# print ('episode {} : {}, {}, {} '.format(ep_num, novel_sub_title, novel_sub_url,novel_sub_update))
				# print (chapter_json)
				ep_num = ep_num+1
		# print ("end_of_Page:",get_page_num, _load_url ,"#-----")
	# print (chapter_json_name)
	return (contents_json)

def create_html_file(list_dict,f_html):


	###################################################
	## 出力用　HTML HEADER

	html_head = """
	<!DOCTYPE html>
	<html lang=ja>
	<html><head><title>{}(id:{})</title></head>
	<body>
	<h1>目次</h1>
	""".format(list_dict['title'],list_dict['id']).strip()

	###################################################
	## 出力用　HTML FOOTER

	html_footer = """
	</body>
	</html>
	"""
	###################################################
	

	print (html_head, file=f_html)

	print ("<h2>" , list_dict['title'] , " (id:",list_dict['id'],") </h2>" , file=f_html)
	print ("<h2> by <a href=\"" , load_url, "\">" , list_dict['AutherName'] , "</a> </h2>" , file=f_html)


	for chap_list_key in list_dict:
		if ("Chapters_" in chap_list_key):
			ep_arry = (list_dict[chap_list_key])	
			# print (ep_arry)
			print ('<h3>CHapter: {} {}</h3>'.format(ep_arry['chp_num'], ep_arry['ChapterName']), file=f_html)
			# print ('<ul>')
			for ep_info in ep_arry['Episode']:
				print ('<li>Episode:{} <a href="{}">{}</a> /{}</li>'.format(ep_info['ep_num'], ep_info['url'], ep_info['title'], ep_info['publishedAt']), file=f_html)
			print ('</ul>', file=f_html)
	print (html_footer, file=f_html)


class GetPagerContents():
	def __init__(self,soup):
		self.__soup = soup

	# def get_page_counts(self):
	# 	novel_main_contents = (self.__soup.find("div" , class_= "c-pager"))
	# 	last_page_line = (novel_main_contents.find("a", class_="c-pager__item c-pager__item--last"))
	# 	last_page_url = last_page_line["href"]
	# 	last_page_num = last_page_url.split('?')[1].split('=')[1]
	#	return (last_page_num)
	# 	#	return (novel_main_contents)


def main():


	novel_page = GetPagerContents(soup)

	

	#########################
	## 作品情報取得          ##
	#########################
	print ("Title.--------------------------------")
	print ("All Page Count : ",get_page_counts())
	page_num = (get_page_counts())

	novel_series_name = get_novel_base_info()[0]
	novel_title = get_novel_base_info()[1]
	novel_auther =get_novel_base_info()[2]
	print ("シリーズ名:", novel_series_name )
	print ("タイトル:", novel_title )
	print ("作者:", novel_auther )

	print("#################")
	#########################
	## 目次リストの取得(JSON)       ##
	#########################
	list_dict = get_all_pages(page_num,novel_series_name,novel_title,novel_auther)

	with open(json_filename, 'w') as f:
		print (json.dumps(get_all_pages(page_num,novel_series_name,novel_title,novel_auther),indent=4, ensure_ascii=False) , file=f)
		f.close()

		# with open(json_filename) as f:
		# 	contents = f.read()
		# 	print(contents)  # hello

	with open(html_filename, 'w') as f_html:
		create_html_file(list_dict,f_html)
		f.close()


main()
