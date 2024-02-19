import requests
import json
import sys
from bs4 import BeautifulSoup

args = sys.argv

# print(args[1])
# print(len(args))

if 2 <= len(args):
	if args[1].isdigit():
		novel_id = args[1]
	else:
		print('Argument is not digit')
else:
	print('Arguments are too short')

kakuyomu_url = "https://kakuyomu.jp"
load_url = kakuyomu_url + "/works/" + novel_id
html = requests.get(load_url)
soup = BeautifulSoup(html.content, "html.parser")

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


s = (soup.find(id="__NEXT_DATA__").text)
j = json.loads(s)

rec01 = (j["props"]["pageProps"]["__APOLLO_STATE__"])

work_id = (j["query"]["workId"])
work_title: str = ""

###################################################
## 出力用　HTML HEADER

html_head = """
<html><head><title>id: {title_id}</title></head>
<body>
<h1>目次</h1>
""".format(title_id=work_id).strip()

###################################################
## 出力用　HTML FOOTER

html_footer = """
</body>
</html>
"""
###################################################


def get_work_info():
	for key in rec01:
		if ("Work:" in key):
			# print(key)
			if (work_id == (j["props"]["pageProps"]["__APOLLO_STATE__"][key]["id"])):
				work_title =(j["props"]["pageProps"]["__APOLLO_STATE__"][key]["title"])
				# work_id =(j["props"]["pageProps"]["__APOLLO_STATE__"][key]["id"])
				print ("<h2>" +  work_title + " (id:" + work_id + ") </h2>" )

def get_episode_info():
	for key in rec01:
		if ("Episode" in key):
			# print(key)
			episode_title =(j["props"]["pageProps"]["__APOLLO_STATE__"][key]["title"])
			episode_id =(j["props"]["pageProps"]["__APOLLO_STATE__"][key]["id"])

			print ("<ul>")
			print ("<li><a href=\"" + kakuyomu_url + "/works/" + work_id + "/episodes/" + episode_id + "\">" + episode_title + "</a><br></li>" )
			print ("</ul>")

def get_chapter_info():
	for chap_list_key in rec01:
		# print (chap_list_key)
		if ("TableOfContentsChapter" in chap_list_key):
			cont_chapter_top =(j["props"]["pageProps"]["__APOLLO_STATE__"][chap_list_key]["episodeUnions"][0]["__ref"])
			cont_chapter_list =(j["props"]["pageProps"]["__APOLLO_STATE__"][chap_list_key]["episodeUnions"])
			cont_chapter_id =(j["props"]["pageProps"]["__APOLLO_STATE__"][chap_list_key]["id"])
			print (cont_chapter_id,cont_chapter_top)
			print (cont_chapter_list)
		else:
			pass
			# 	chapter_title =(j["props"]["pageProps"]["__APOLLO_STATE__"][key]["title"])
			# 	chapter_id =(j["props"]["pageProps"]["__APOLLO_STATE__"][key]["id"])
			# 	print (chapter_id, chapter_title)

def get_chapter_title():
	for key in rec01:
		if ("Chapter" in key):
			# print(key)
			# print(key.find("Chapter"))
			if(key.find("Chapter") == 0):
				chapter_title =(j["props"]["pageProps"]["__APOLLO_STATE__"][key]["title"])
				chapter_id =(j["props"]["pageProps"]["__APOLLO_STATE__"][key]["id"])
				cont_chapter_list =(j["props"]["pageProps"]["__APOLLO_STATE__"]["TableOfContentsChapter:" + chapter_id]["episodeUnions"])

				# print (key,chapter_id, chapter_title)
				print ("<h3>" + chapter_title + "</h3>")
				print ("<ul>")
				for list_key in cont_chapter_list:
					# print (list_key)
					ep_key=list_key["__ref"]
					# print (ep_key)
					get_title_element(ep_key)
				print ("</ul>")


			# 	print (chapter_id, chapter_title)

def get_title_element(ep_key):
	episode_title =(j["props"]["pageProps"]["__APOLLO_STATE__"][ep_key]["title"])
	episode_id =(j["props"]["pageProps"]["__APOLLO_STATE__"][ep_key]["id"])
	print ("<li><a href=\"" + kakuyomu_url + "/works/" + work_id + "/episodes/" + episode_id + "\">" + episode_title + "</a><br></li>" )

def main():
	print (html_head)
	get_work_info()
	# print ( work_title + " (id:" + work_id + ")" )


	## test チャプター有り無し判定により出力内容を変更する
	if(len(j["props"]["pageProps"]["__APOLLO_STATE__"]["Work:" + work_id]["tableOfContents"])> 1):
		# print("チャープターあり")
		get_chapter_title()
	else:
		# print("チャープターなし")
		get_episode_info()

	# get_chapter_info()
	# get_episode_info()
	print (html_footer)


main()