import requests
import json
import datetime
import sys
from bs4 import BeautifulSoup

args = sys.argv

# print(args[1])
# print(len(args))

# if 2 <= len(args):
# 	if args[1].isdigit():
# 		novel_id = args[1]
# 	else:
# 		print('Argument is not digit')
# else:
# 	print('Arguments are too short')

source_dir="../../json_source"
source_file="daysneo_da59da23660b4fa346e5717aed10e147.html"

novel_url = "https://ncode.syosetu.com"
novel_id = "n6453iq" # 春暁記
# novel_id = "n3289ds" # のんびり農家


## なろうサイトではUAが存在していないとデータが取得できない(403で返る）ためにUAを設定
ua_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0"}


# https://ncode.syosetu.com/n6453iq/

load_url = novel_url + "/" + novel_id + "/"

# source_file_name = source_dir + "/" + source_file
html = requests.get(load_url , headers = ua_headers)
soup = BeautifulSoup(html.content, "html.parser")

# タイトルと説明を抽出してJSON形式に変換
json_data = []
id_counter = 1

# ## URLから正常にhtmlが取得できるかのテスト
# print ("URL.--------------------------------")
# print(load_url)
# print ("soup.--------------------------------")
# print(soup)
# print ("end_of_soup.--------------------------------")


# with open(source_file_name) as f:
# 	html = f.read()

# soup = BeautifulSoup(html, "html.parser")
# requests でソースを取得する場合は”．content”を付ける必要がある



# filename = '../../html/' + novel_id + '.html'

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

def get_page_counts():
	novel_page_contents = (soup.find("div" , class_= "c-pager"))
	last_page_line = (novel_page_contents.find("a", class_="c-pager__item c-pager__item--last"))
	last_page_url = last_page_line["href"]
	last_page_num = last_page_url.split('?')[1].split('=')[1]
	# print("Section.--------------------------------")
	# print (novel_main_contents)
	# print("Line.--------------------------------")
	# print (last_page_line)
	# print("num.--------------------------------")
	# print (last_page_url)
	return (last_page_num)

def get_all_pages(page_num):
	ep_num=int(1)
	page_num = int(page_num) + 1
	for get_page_num in range(1, page_num):
		print ("Page:",get_page_num,"#-----")
		_load_url = "{}/{}/?p={}".format(novel_url,novel_id,get_page_num)
		l_html = requests.get(_load_url , headers = ua_headers)
		l_soup = BeautifulSoup(l_html.content, "html.parser")
		novel_main_contents = (l_soup.find("div" , class_= "p-eplist"))
		# novel_ep_contents_list = (novel_main_contents.select("div" , class_= "p-eplist__subtitle"))
		novel_ep_contents_list = (novel_main_contents.select('a'))
		for key in novel_ep_contents_list:
			# print ("#",key)	
			novel_sub_url = (novel_url + key.get("href"))
			novel_sub_title = key.text.strip()
			print ('episode {} : {},{}'.format(ep_num, novel_sub_title, novel_sub_url))
			ep_num = ep_num+1
		# print ("end_of_Page:",get_page_num, _load_url ,"#-----")



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

# print (content_title)
# print (novel_main_contents)

###############
# findやfind_allの引数に「属性名='値'」を渡します。
# ※classを検索するときにはアンダースコアを付与します（class_）。
# ※classキーワードがPythonの予約語のため。
###############
##content_li = (s.find_all("li"), s.find("h4"))

## Get Novel base info
# novel_title = novel_head_contents.find("h2")

# print (novel_title)


# for content_li in (novel_main_contents.select("li li , li h4")):
# 	content_link = content_li.find('a')
# 	if content_link is None:
# 		content_text = content_li.text
# 		content_url = ""
# 		# continue
# 	else:
# 		content_url = content_link.get("href")
# 		content_text = content_link.text
# 	# print("1.--------------------------------")
# 	# print(content_li.text)
# 	# print("2.--------------------------------")
# 	# print(content_link)
# 	print(content_text,".--------------------------------")
# 	print(novel_url + content_url)



# s = (soup.find(id="__NEXT_DATA__").text)
# j = json.loads(s)

# rec01 = (j["props"]["pageProps"]["__APOLLO_STATE__"])

# work_id = (j["query"]["workId"])
# work_title: str = ""

###################################################
## 出力用　HTML HEADER

# html_head = """
# <!DOCTYPE html>
# <html lang=ja>
# <html><head><title>id: {title_id}</title></head>
# <body>
# <h1>目次</h1>
# """.format(title_id=work_id).strip()

###################################################
## 出力用　HTML FOOTER

html_footer = """
</body>
</html>
"""
###################################################


def main():


	novel_page = GetPagerContents(soup)
	print ("Title.--------------------------------")
	print (get_page_counts())
	page_num = (get_page_counts())

	get_all_pages(page_num)


	print("#################")



main()
