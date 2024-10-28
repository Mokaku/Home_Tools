import requests
import json
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

kakuyomu_url = "https://kakuyomu.jp"
load_url = kakuyomu_url + "/works/" + novel_id
# html = requests.get(load_url)

# soup = BeautifulSoup(html.content, "html.parser")
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


# filename = '../../novel_database/' + novel_id + '_test04.json'

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

# html_footer = """
# </body>
# </html>
# """
###################################################

def main():
	print("test")


main()