# import datetime
import json
import sys
import os
import re

from bs4 import BeautifulSoup

import requests

args = sys.argv

# print(args[1])
# print(len(args))

if 2 <= len(args):
    novel_id = args[1]
    # if args[1].isdigit():
    #     novel_id = args[1]
    # else:
    #     print('Argument is not digit')
else:
    print('Arguments are too short')
    sys.exit(1) # 修正: 引数不足時は後続処理を止め、安全に終了させる

source_dir = "../../json_source"
source_file = "daysneo_da59da23660b4fa346e5717aed10e147.html"

novel_url = "https://ncode.syosetu.com"
prefix = "narou_"

# なろうサイトではUAが存在していないとデータが取得できない(403で返る）ためにUAを設定
ua_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0"}

#########################
# なろう小説ID(for test)##
#########################
# novel_id = "n6453iq" # 春暁記
# novel_id = "n3289ds" # のんびり農家
# novel_id = "n1146do" # 捨て子になりましたが、魔法のおかげで大丈夫そうです
# novel_id = "2710db" #とんでもスキルで異世界放浪メシ
# novel_id = "n9636x" #薬屋のひとりごと

# https://ncode.syosetu.com/n6453iq/

load_url = f"{novel_url}/{novel_id}/"

# source_file_name = source_dir + "/" + source_file
html = requests.get(load_url, headers=ua_headers)
soup = BeautifulSoup(html.content, "html.parser")

# タイトルと説明を抽出してJSON形式に変換
json_data = []
id_counter = 1

# soup = BeautifulSoup(html, "html.parser")
# requests でソースを取得する場合は”．content”を付ける必要がある

json_filename = f'../../html/narou/json/{prefix}{novel_id}.json'
html_filename = f'../../html/narou/{prefix}{novel_id}.html'

###################################################
# bt4 module 使い方メモ
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
    novel_series = soup.find(class_="p-novel__series")
    # 修正: Pythonらしい条件分岐でスッキリと記述 (前回不足していた is を追加)
    novel_series_name = "N/A" if novel_series is None else novel_series.text.strip()
    # print (novel_series_name)
    novel_title = soup.find(class_="p-novel__title").text.strip()
    # print (novel_title)
    novel_auther = soup.find(class_="p-novel__author").text.strip()
    return [novel_series_name, novel_title, novel_auther]


def get_page_counts():
    novel_page_contents = soup.find("div", class_="c-pager")
    if novel_page_contents is None:
        last_page_num = 1
    else:
        last_page_line = novel_page_contents.find("a", class_="c-pager__item c-pager__item--last")
        last_page_url = last_page_line["href"]
        last_page_num = last_page_url.split('?')[1].split('=')[1]
    # debug ###
    # print("Section.--------------------------------")
    # print (novel_main_contents)
    # print("Line.--------------------------------")
    # print (last_page_line)
    # print("num.--------------------------------")
    # print (last_page_url)
    return int(last_page_num) # 修正: 数値として返すよう明示的にキャスト


def get_all_pages(page_num, novel_series_name, novel_title, novel_auther):
    ep_num = 1
    chp_num = 1
    page_num = int(page_num) + 1
    contents_json = {"__typename": "Story", "id": novel_id, "serieis": novel_series_name, "title": novel_title, "AutherName": novel_auther}

    # Chapterの無いNovelのためにます、 ep_list とchapter_jsonを初期化しておく。
    chapter_json_name = "Chapters_1"
    ep_list = []
    chapter_json = {"__typename": "Chapter", "chp_num": "", "ChapterName": "", "Episode": ep_list}

    for get_page_num in range(1, page_num):
        # print ("Page:",get_page_num,"#-----")
        # 修正: f-stringの適用
        _load_url = f"{novel_url}/{novel_id}/?p={get_page_num}"
        l_html = requests.get(_load_url, headers=ua_headers)
        l_soup = BeautifulSoup(l_html.content, "html.parser")
        novel_main_contents = l_soup.find("div", class_="p-eplist")
        # novel_ep_contents_list = (novel_main_contents.find("div" , class_= "p-eplist__subtitle"))
        
        # 安全策: 万が一中身が取得できなかったらスキップ
        if not novel_main_contents:
            continue
            
        novel_ep_contents_list = novel_main_contents.find_all(class_=['p-eplist__chapter-title', 'p-eplist__sublist'])
        # print ("-----------------------")
        # print (novel_ep_contents_list)
        # novel_ep_contents_list = (novel_main_contents.select('a'))

        for key in novel_ep_contents_list:
            # print ("### -----------------------")
            # print ("#1",key)
            # print ("------------")
            if key.find(class_="p-eplist__subtitle") is None:
                key_cp_title = key.text.strip()
                # 修正: f-stringの適用
                chapter_json_name = f'Chapters_{chp_num}'
                # Chapterの存在するNovelの場合、章分割のために ep_list とchapter_jsonを再度初期化。
                ep_list = []
                chapter_json = {"__typename": "Chapter", "chp_num": chp_num,
                                "ChapterName": key_cp_title, "Episode": ep_list}
                # print('Chapter {} {}'.format(chp_num,key_cp_title))
                # print( chapter_json )
                chp_num += 1
            else:
                key_link = key.find(class_="p-eplist__subtitle")
                key_update_date = key.find(class_="p-eplist__update")
                # print ("#2",key_link," / ",key_update_date)
                # print ("------------")
                # 修正: f-stringの適用
                novel_sub_url = f'{novel_url}{key_link.get("href")}'
                novel_sub_title = key_link.text.strip()
                novel_sub_update = key_update_date.text.strip().replace("\n", "")
                ep_list.append({"__typename": "Episode", "ep_num": ep_num, "url": novel_sub_url,
                                "title": novel_sub_title, "publishedAt": novel_sub_update})
                chapter_json["Episode"] = ep_list
                contents_json[chapter_json_name] = chapter_json
                # print ('episode {} : {}, {}, {} '.format(ep_num, novel_sub_title, novel_sub_url,novel_sub_update))
                # print (chapter_json)
                ep_num += 1
        # print ("end_of_Page:",get_page_num, _load_url ,"#-----")
    # print (chapter_json_name)
    return contents_json


def create_html_file(list_dict, f_html):

    ###################################################
    # 出力用　HTML HEADER

    # 修正: f-stringの適用
    html_head = f"""
    <!DOCTYPE html>
    <html lang=ja>
    <html><head><title>{list_dict['title']}(id:{list_dict['id']})</title></head>
    <body>
    <h1>目次</h1>
    """.strip()

    ###################################################
    # 出力用　HTML FOOTER

    html_footer = """
    </body>
    </html>
    """
    ###################################################

    print(html_head, file=f_html)

    # 修正: f-stringの適用
    print(f"<h2> {list_dict['title']} (id: {list_dict['id']}) </h2>", file=f_html)
    print(f"<h2> by <a href=\"{load_url}\">{list_dict['AutherName']}</a> </h2>", file=f_html)

    for chap_list_key in list_dict:
        if "Chapters_" in chap_list_key:
            ep_arry = list_dict[chap_list_key]
            # print (ep_arry)
            # 修正: f-stringの適用
            print(f"<h3>Chapter: {ep_arry['chp_num']} {ep_arry['ChapterName']}</h3>", file=f_html)
            
            # 修正: 過去コメントアウトされていた<ul>タグを復活(これがないとリストが崩れるため)
            print('<ul>', file=f_html) 
            
            for ep_info in ep_arry['Episode']:
                # 修正: f-stringの適用
                print(f"<li>Episode:{ep_info['ep_num']} <a href=\"{ep_info['url']}\">{ep_info['title']}</a> /{ep_info['publishedAt']}</li>", file=f_html)
            print('</ul>', file=f_html)
            
    print(html_footer, file=f_html)


class GetPagerContents():
    def __init__(self, soup):
        self.__soup = soup


def main():

    # novel_page = GetPagerContents(soup)

    #########################
    # 作品情報取得          ##
    #########################
    print("--------------------------------")
    
    # 修正: 関数を一度だけ呼んで変数に格納（無駄な重複処理を回避）
    page_num = get_page_counts()
    print("All Page Count : ", page_num)

    # 修正: 同様に一度だけ呼び出す
    base_info = get_novel_base_info()
    novel_series_name = base_info[0]
    novel_title = base_info[1]
    novel_auther = base_info[2]
    
    print("タイトル:", novel_title)
    print("シリーズ名:", novel_series_name)
    print("作者:", novel_auther)

    print("#################")
    #########################
    # 目次リストの取得(JSON)       ##
    #########################
    
    # 最も重い処理(HTTPリクエスト群)を1回だけ実行して変数へ格納
    list_dict = get_all_pages(page_num, novel_series_name, novel_title, novel_auther)

    # ---------------------------------------------------------
    # 追加: 更新判定と narou_all_novel_id.list の更新処理
    # ---------------------------------------------------------
    
    # 1. 取得したデータから最新の更新日時を抽出
    latest_date = ""
    for chap_key in list_dict:
        if chap_key.startswith("Chapters_"):
            ep_arry = list_dict[chap_key]
            if ep_arry.get("Episode"):
                # 最新のエピソードの更新日を保持（一番最後が最新）
                latest_date = ep_arry["Episode"][-1]["publishedAt"]

    # 2. リストファイルを読み込み、更新チェック
    list_dir = "../../novel_database/"
    list_file = "narou_all_novel_id.list"
    list_path = os.path.join(list_dir, list_file)
    
    is_updated = True # 初期値は更新あり

    if os.path.exists(list_path):
        with open(list_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        new_lines = []
        for line in lines:
            if line.startswith(f"{novel_id},"):
                # "id, flag, title[, date]" という構成を前提にパース
                parts = line.split(',', 2)
                if len(parts) == 3:
                    # すでに同じ最新日時が記録されている場合は更新スキップ
                    if latest_date and (latest_date in parts[2]):
                        is_updated = False
                        new_lines.append(line)
                    else:
                        # 既存の日付を正規表現で探して置換するか、追記する
                        sub_parts = parts[2].rsplit(',', 1)
                        if len(sub_parts) == 2 and re.search(r'\d{4}/\d{2}/\d{2}', sub_parts[1]):
                            # 既に日付カラムがある場合は置換
                            new_line = f"{parts[0]},{parts[1]},{sub_parts[0]}, {latest_date}\n"
                        else:
                            # 初回追記：末尾の改行を削って、日付カラムを追加
                            clean_title = parts[2].rstrip('\n')
                            new_line = f"{parts[0]},{parts[1]},{clean_title}, {latest_date}\n"
                        new_lines.append(new_line)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
                
        # 更新が確認された場合のみ、リストファイルを上書き更新
        if is_updated:
            os.makedirs(list_dir, exist_ok=True)
            with open(list_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
    else:
        # リストファイルがない場合は警告を出しつつ、出力自体は行う
        print(f"警告: リストファイルが見つかりません ({list_path})")

    # 3. 更新有無に応じたHTML/JSONの出力
    if is_updated:
        print(f"【更新あり】コンテンツに更新が検出されました (最終更新: {latest_date})。HTMLとJSONを出力します。")
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            print(json.dumps(list_dict, indent=4, ensure_ascii=False), file=f)

        with open(html_filename, 'w', encoding='utf-8') as f_html:
            create_html_file(list_dict, f_html)
    else:
        print(f"【更新なし】コンテンツに変更はありませんでした (最終更新: {latest_date})。出力処理をスキップします。")


main()

