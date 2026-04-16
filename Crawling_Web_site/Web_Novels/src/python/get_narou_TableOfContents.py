# import datetime
import json
import sys
import os
import re
import sqlite3
import argparse

from bs4 import BeautifulSoup
import requests

# ==========================================
# === 引数と管理形式の設定 ===
# ==========================================
# コマンドライン引数の設定
parser = argparse.ArgumentParser(description="なろう小説の目次を取得・更新します")
parser.add_argument("novel_id", type=str, help="取得する小説のID（例: n2732lu）")
parser.add_argument("--mode", type=str, choices=["sqlite", "csv"], default="sqlite", 
                    help="管理形式の指定 (デフォルト: sqlite)")
args = parser.parse_args()



## args = sys.argv
# print(args[1])
# print(len(args))

## if 2 <= len(args):
##     novel_id = args[1]
## else:
##     print('Arguments are too short')
##     sys.exit(1) # 修正: 引数不足時は後続処理を止め、安全に終了させる

# ==========================================
# === 管理形式の設定（ここでモードを切り替えます）===
# ==========================================
# 引数から値を取得
novel_id = args.novel_id

MANAGEMENT_MODE = args.mode 
SITE_TYPE = "narou"         # DB用のサイト識別子

# ファイルパスの定義
LIST_DIR = "../../novel_database/"
CSV_FILE_NAME = "narou_all_novel_id.list"
DB_FILE_NAME = "all_novels_database_01.db"

CSV_FILE_PATH = os.path.join(LIST_DIR, CSV_FILE_NAME)
DB_FILE_PATH = os.path.join(LIST_DIR, DB_FILE_NAME)
# ==========================================

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
    contents_json = {"__typename": "Story", "id": novel_id, "series": novel_series_name, "title": novel_title, "AuthorName": novel_auther}

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
    print(f"<h2> by <a href=\"{load_url}\">{list_dict['AuthorName']}</a> </h2>", file=f_html)

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


# ==========================================
# データベース / CSV 管理用関数群
# ==========================================

def manage_with_sqlite(db_path, target_novel_id, site_type, title, latest_date, is_deleted=False):
    """
    SQLiteを用いて更新日時を管理し、更新の有無を返す関数
    """
    is_updated = True
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # DBに接続（ファイルがない場合は自動作成されます）
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # テーブル作成（初回のみ実行される）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS novels (
            novel_id TEXT PRIMARY KEY,
            site_type TEXT,
            flag INTEGER,
            title TEXT,
            last_update TEXT
        )
    ''')

    if is_deleted:
        print(f"!!! [SQLITE] コンテンツ不在を検知。ID: {target_novel_id} の取得フラグを 0 (停止) に更新します。")
        cursor.execute('UPDATE novels SET flag = 0 WHERE novel_id = ?', (target_novel_id,))
        is_updated = False
    else:
        # 現在登録されているデータを検索
        cursor.execute('SELECT last_update, flag FROM novels WHERE novel_id = ?', (target_novel_id,))
        row = cursor.fetchone()
        if row:
            db_last_update = row[0]
            # 更新日が同じならスキップ判定
            if latest_date and db_last_update == latest_date:
                is_updated = False
            else:
                # 日付が変わっていればレコードを更新
                cursor.execute('UPDATE novels SET title = ?, last_update = ?, flag = 1 WHERE novel_id = ?', 
                               (title, latest_date, target_novel_id))
        else:
            # 新規登録（CSVに合わせたデフォルトフラグとして 1 を設定）
            cursor.execute('INSERT INTO novels (novel_id, site_type, flag, title, last_update) VALUES (?, ?, ?, ?, ?)',
                           (target_novel_id, site_type, 1, title, latest_date))

    # 変更を保存して接続を閉じる
    conn.commit()
    conn.close()
    return is_updated


def manage_with_csv(list_path, target_novel_id, latest_date, is_deleted=False):
    """
    CSV(.list)形式を用いて更新日時を管理し、更新の有無を返す関数
    （これまでの処理をそのまま関数化したものです）
    """
    is_updated = True

    if not os.path.exists(list_path):
        print(f"警告: リストファイルが見つかりません ({list_path})")
        return False

    with open(list_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
            
    new_lines = []
    found = False
    for line in lines:
        if line.startswith(f"{target_novel_id},"):
            found = True
            parts = line.split(',', 2)

            if is_deleted:
                print(f"!!! [CSV] コンテンツ不在を検知。ID: {target_novel_id} の取得フラグを 0 に更新します。")
                new_line = f"{parts[0]}, 0, {parts[2]}" if len(parts) >= 3 else line
                new_lines.append(new_line)
                is_updated = False

            else:
                if len(parts) == 3:
                    if latest_date and (latest_date in parts[2]):
                        is_updated = False
                        new_lines.append(line)
                    else:
                        sub_parts = parts[2].rsplit(',', 1)
                        # カクヨムとなろうで正規表現が違うため、環境に合わせて柔軟にマッチさせます
                        if len(sub_parts) == 2 and (re.search(r'\d{4}/\d{2}/\d{2}', sub_parts[1]) or re.search(r'\d{4}年\d{2}月\d{2}日', sub_parts[1])):
                            new_line = f"{parts[0]},{parts[1]},{sub_parts[0]}, {latest_date}\n"

                        else:
                            clean_title = parts[2].rstrip('\n')
                            new_line = f"{parts[0]},{parts[1]},{clean_title}, {latest_date}\n"
                        new_lines.append(new_line)
                    else:
                        new_lines.append(line)
        else:
            new_lines.append(line)
            
    if found or is_deleted:
        os.makedirs(os.path.dirname(list_path), exist_ok=True)
        with open(list_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    return is_updated

# ==========================================

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

    # ★ コンテンツ削除のチェック
    if novel_title is None or novel_title == "" or "エラー" in novel_title:
        print(f"\n################################################")
        print(f"警告: なろうID {novel_id} のタイトルが取得できません。")
        print(f"削除または非公開の可能性があります。フラグを停止に更新します。")
        print(f"################################################")

        if MANAGEMENT_MODE == "sqlite":
            manage_with_sqlite(DB_FILE_PATH, novel_id, SITE_TYPE, None, None, is_deleted=True)
        elif MANAGEMENT_MODE == "csv":
            manage_with_csv(CSV_FILE_PATH, novel_id, None, is_deleted=True)
        
        sys.exit(0) # 以降のスクレイピング・ファイル出力を中断
    
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

    # 2. 設定されたモードに応じて、DBまたはCSVの更新関数を呼び出す
    if MANAGEMENT_MODE == "sqlite":
        print(f"[SQLiteモードで実行中] DB: {DB_FILE_NAME}")
        is_updated = manage_with_sqlite(DB_FILE_PATH, novel_id, SITE_TYPE, novel_title, latest_date)
    elif MANAGEMENT_MODE == "csv":
        print(f"[CSVモードで実行中] List: {CSV_FILE_NAME}")
        is_updated = manage_with_csv(CSV_FILE_PATH, novel_id, latest_date)
    else:
        print("エラー: MANAGEMENT_MODE の設定が不正です。")
        sys.exit(1)


    # 3. 更新有無に応じたHTML/JSONの出力
    if is_updated:
        print(f"【更新あり】コンテンツに更新が検出されました (最終更新: {latest_date})。HTMLとJSONを出力します。")

        os.makedirs(os.path.dirname(json_filename), exist_ok=True)
        os.makedirs(os.path.dirname(html_filename), exist_ok=True)
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            print(json.dumps(list_dict, indent=4, ensure_ascii=False), file=f)

        with open(html_filename, 'w', encoding='utf-8') as f_html:
            create_html_file(list_dict, f_html)
    else:
        print(f"【更新なし】コンテンツに変更はありませんでした (最終更新: {latest_date})。出力処理をスキップします。")


main()

