import datetime
import json
import os
import sys
import re  # 追加: 日付の正規表現チェック用
import sqlite3
import argparse

from bs4 import BeautifulSoup
import requests

# ==========================================
# === 引数と管理形式の設定 ===
# ==========================================
# コマンドライン引数の設定
parser = argparse.ArgumentParser(description="カクヨム!の目次を取得・更新します")
parser.add_argument("novel_id", type=str, help="取得する小説のID（例: 16817330667341551839）")
parser.add_argument("--mode", type=str, choices=["sqlite", "csv"], default="sqlite", 
                    help="管理形式の指定 (デフォルト: sqlite)")
args = parser.parse_args()

## args = sys.argv

# print(args[1])
# print(len(args))

## if 2 <= len(args):
##     if args[1].isdigit():
##         novel_id = args[1]
##     else:
##         print('Argument is not digit')
##         sys.exit(1)  # 修正: エラー時は後続処理を止め、安全に終了させる
## else:
##     print('Arguments are too short')
##     sys.exit(1)  # 修正: エラー時は後続処理を止め、安全に終了させる

# ==========================================
# === 管理形式の設定（ここでモードを切り替えます）===
# ==========================================
# 引数から値を取得
novel_id = args.novel_id
MANAGEMENT_MODE = args.mode  # ← args.mode に修正します
SITE_TYPE = "kakuyomu"         # DB用のサイト識別子

# ファイルパスの定義
LIST_DIR = "../../novel_database/"
CSV_FILE_NAME = "kakuyomu_all_novel_id.list"
DB_FILE_NAME = "all_novels_database_01.db"

CSV_FILE_PATH = os.path.join(LIST_DIR, CSV_FILE_NAME)
DB_FILE_PATH = os.path.join(LIST_DIR, DB_FILE_NAME)
# ==========================================


kakuyomu_url = "https://kakuyomu.jp"
kakuyomu_user_page_url = "https://kakuyomu.jp/users"
prefix = "kakuyomu_"

load_url = kakuyomu_url + "/works/" + novel_id

# 2026年現在のブラウザに見せかけるためのヘッダー
headers = {
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

html = requests.get(load_url, headers=headers)
soup = BeautifulSoup(html.content, "html.parser")

filename = '../../html/' + prefix + novel_id + '.html'
# home_dir = '/home/htobe'
home_dir = os.environ['HOME']

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

## if soup.find(id="__NEXT_DATA__"):
##     print("\n..... Data Load OK")
##     j = json.loads(soup.find(id="__NEXT_DATA__").text)  # type: ignore
## 
##     rec01 = (j["props"]["pageProps"]["__APOLLO_STATE__"])
##     work_id = (j["query"]["workId"])
##     work_title: str = ""

if soup.find(id="__NEXT_DATA__"):
    print("\n..... Data Load OK")
    j = json.loads(soup.find(id="__NEXT_DATA__").text)  # type: ignore

    rec01 = (j["props"]["pageProps"]["__APOLLO_STATE__"])
    
    # 修正: JSONから取得せず、引数で渡された novel_id をそのまま利用する
    work_id = novel_id 
    
    work_title: str = ""

else:
    print("\n############\nNovel ID:", novel_id, "\nThis Novel Contents does not Exist\n############")
    sys.exit(0)


class GetBaseNobelInfo():

    def __init__(self, work_id, rec01):
        self.__work_id = work_id
        self.__rec01 = rec01
        # 修正: ループ検索を避けるため、対象のキーを初期化時に確定させておく
        self.__work_key = f"Work:{self.__work_id}"
        self.__auther_id = self.get_auther_id()

    def only_get_work_title(self):
        # 修正: forループとjへの依存を排除。辞書のgetメソッドで安全・高速に取得
        return self.__rec01.get(self.__work_key, {}).get("title")

    def get_auther_id(self):
        # 修正: forループとjへの依存を排除。
        return self.__rec01.get(self.__work_key, {}).get("author", {}).get("__ref")

    def only_get_work_last_update(self):
        # 修正: forループとjへの依存を排除。
        last_episode_published_at = self.__rec01.get(self.__work_key, {}).get("lastEpisodePublishedAt")
        if last_episode_published_at:
            last_update_date = datetime.datetime.fromisoformat(last_episode_published_at).strftime('%Y年%m月%d日 %H:%M')
            return last_update_date
        return ""

    def only_get_auther_activity_name(self):
        # 修正: forループとjへの依存を排除。
        return self.__rec01.get(self.__auther_id, {}).get("activityName")

    def only_get_auther_name(self):
        # 修正: forループとjへの依存を排除。
        return self.__rec01.get(self.__auther_id, {}).get("name")


## def get_episode_info(f):
##     print("<ul>", file=f)
##     for key in rec01:
##         if ("Episode:" in key):
##             # print(key)
##             episode_title = (j["props"]["pageProps"]["__APOLLO_STATE__"][key]["title"])
##             episode_id = (j["props"]["pageProps"]["__APOLLO_STATE__"][key]["id"])
##             episode_update_isodate = (j["props"]["pageProps"]["__APOLLO_STATE__"][key]["publishedAt"])
##             episode_update_date = datetime.datetime.fromisoformat(episode_update_isodate).strftime('%Y年%m月%d日 %H:%M')
## 
##             print("<li><a href=\"" + kakuyomu_url + "/works/" + work_id
##                   + "/episodes/" + episode_id + "\">" + episode_title
##                   + "</a> [" + episode_update_date + "] <br></li>", file=f)
##     print("</ul>", file=f)

def get_episode_info(f, rec01_data, target_work_id, base_url):
    print("<ul>", file=f)
    
    # 新しいJSON構造に合わせて "TableOfContentsChapter:" から順番にエピソードを取得
    toc_key = "TableOfContentsChapter:"
    if toc_key in rec01_data:
        episode_list = rec01_data[toc_key].get("episodeUnions", [])
        for ep in episode_list:
            ep_key = ep["__ref"]  # 例: "Episode:16818093074582369892"
            get_title_element(ep_key, f, rec01_data, target_work_id, base_url)
    else:
        # 万が一見つからない場合のフォールバック（旧ロジック）
        for key in rec01_data:
            if key.startswith("Episode:"):
                get_title_element(key, f, rec01_data, target_work_id, base_url)
                
    print("</ul>", file=f)


def get_title_element(ep_key, f, rec01_data, target_work_id, base_url):
    # 修正: 冗長だった j["props"]["pageProps"]["__APOLLO_STATE__"] を rec01 の直接参照へ変更
    episode_title = rec01_data[ep_key]["title"]
    episode_id = rec01_data[ep_key]["id"]
    episode_update_isodate = rec01_data[ep_key]["publishedAt"]
    episode_update_date = datetime.datetime.fromisoformat(episode_update_isodate).strftime('%Y年%m月%d日 %H:%M')

    # 修正: + 結合を f-string に変更し、HTMLとしての見通しを改善
    print(f'<li><a href="{base_url}/works/{target_work_id}/episodes/{episode_id}">{episode_title}</a> [{episode_update_date}] <br></li>', file=f)


# def get_chapter_info():
#     for chap_list_key in rec01:
#         # print (chap_list_key)
#         if ("TableOfContentsChapter:" in chap_list_key):
#             cont_chapter_top = (j["props"]["pageProps"]["__APOLLO_STATE__"][chap_list_key]["episodeUnions"][0]["__ref"])
#             cont_chapter_list = (j["props"]["pageProps"]["__APOLLO_STATE__"][chap_list_key]["episodeUnions"])
#             cont_chapter_id = (j["props"]["pageProps"]["__APOLLO_STATE__"][chap_list_key]["id"])
#             print(cont_chapter_id, cont_chapter_top)
#             print(cont_chapter_list)
#         else:
#             pass
#             #     chapter_title = (j["props"]["pageProps"]["__APOLLO_STATE__"][key]["title"])
#             #     chapter_id = (j["props"]["pageProps"]["__APOLLO_STATE__"][key]["id"])
#             #     print (chapter_id, chapter_title)


def get_chapter_title(f, rec01_data, target_work_id, base_url):
    for key in rec01_data:
        if ("Chapter" in key):
            # print(key)
            # print(key.find("Chapter"))
            if (key.find("Chapter") == 0):
                # 修正: 冗長だった j["props"]["pageProps"]["__APOLLO_STATE__"] を 引き渡されたrec01_data の直接参照へ変更
                chapter_title = rec01_data[key]["title"]
                chapter_id = rec01_data[key]["id"]
                cont_chapter_list = rec01_data["TableOfContentsChapter:" + chapter_id]["episodeUnions"]

                # 修正: f-string による文字列組み立て
                print(f"<h3>{chapter_title}</h3>", file=f)
                print("<ul>", file=f)
                for list_key in cont_chapter_list:
                    # print (list_key)
                    ep_key = list_key["__ref"]
                    # print (ep_key)
                    get_title_element(ep_key, f, rec01_data, target_work_id, base_url) #次の関数にリレー
                print("</ul>", file=f)
            #     print (chapter_id, chapter_title)

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
        # コンテンツ削除時の処理: flag を 0 にして更新なしとする
        print(f"!!! [SQLITE] コンテンツ不在を検知。ID: {target_novel_id} の取得フラグを 0 (停止) に更新します。")
        cursor.execute('UPDATE novels SET flag = 0 WHERE novel_id = ?', (target_novel_id,))
        is_updated = False

    else:
        # 現在登録されているデータを検索
        cursor.execute('SELECT last_update, flag FROM novels WHERE novel_id = ?', (target_novel_id,))
        row = cursor.fetchone()
        if row:
            db_last_update = row[0]
            if latest_date and db_last_update == latest_date:
                is_updated = False
            else:
                cursor.execute('UPDATE novels SET title = ?, last_update = ?, flag = 1 WHERE novel_id = ?', 
                               (title, latest_date, target_novel_id))
        else:
            cursor.execute('INSERT INTO novels (novel_id, site_type, flag, title, last_update) VALUES (?, ?, ?, ?, ?)',
                           (target_novel_id, site_type, 1, title, latest_date))

    conn.commit()
    conn.close()
    return is_updated

def manage_with_csv(list_path, target_novel_id, latest_date, is_deleted=False):
    """
    CSV(.list)形式を用いて更新日時を管理し、更新の有無を返す関数
    is_deleted=True の場合、対象の flag を 0 に更新する
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


def main():

    # 1. 取得したデータから作品情報と最新の更新日時を抽出
    novel_info = GetBaseNobelInfo(work_id, rec01)

    print("--------------------------------")
    novel_title = novel_info.only_get_work_title()

    # ★ コンテンツ削除のチェック
    if novel_title is None or novel_title == "" or novel_title == "None":
        print(f"\n################################################")
        print(f"警告: カクヨムID {work_id} のタイトルが取得できません。")
        print(f"コンテンツが削除されている可能性があります。フラグを停止に更新します。")
        print(f"################################################")
        
        if MANAGEMENT_MODE == "sqlite":
            manage_with_sqlite(DB_FILE_PATH, work_id, SITE_TYPE, None, None, is_deleted=True)
        elif MANAGEMENT_MODE == "csv":
            manage_with_csv(CSV_FILE_PATH, work_id, None, is_deleted=True)
        
        sys.exit(0) # 以降のスクレイピング・ファイル出力を中断

    # 通常のノベルデータ更新処理
    novel_auther = novel_info.only_get_auther_activity_name()
    latest_date = novel_info.only_get_work_last_update()
    
    print("タイトル:", novel_title)
    print("作者:", novel_auther)
    print("#################")

    # 2. 設定されたモードに応じて、DBまたはCSVの更新関数を呼び出す
    if MANAGEMENT_MODE == "sqlite":
        print(f"[SQLiteモードで実行中] DB: {DB_FILE_NAME}")
        is_updated = manage_with_sqlite(DB_FILE_PATH, work_id, SITE_TYPE, novel_title, latest_date)
    elif MANAGEMENT_MODE == "csv":
        print(f"[CSVモードで実行中] List: {CSV_FILE_NAME}")
        is_updated = manage_with_csv(CSV_FILE_PATH, work_id, latest_date)
    else:
        print("エラー: MANAGEMENT_MODE の設定が不正です。")
        sys.exit(1)


    # 3. 更新有無に応じたHTMLの出力
    if is_updated:
        print(f"【更新あり】コンテンツに更新が検出されました (最終更新: {latest_date})。HTMLを出力します。")

        # HTML出力用の変数準備
        auther_url = f"{kakuyomu_user_page_url}/{novel_info.only_get_auther_name()}"
        html_head = f"""
        <!DOCTYPE html>
        <html lang=ja>
        <html><head><title>{novel_title}(id:{work_id})</title></head>
        <body>
        <h1>目次</h1>
        """.strip()

        html_footer = """
        </body>
        </html>
        """

        # ブックマーク・DB用情報の出力（既存の動作を維持）
        info_text = '## For Novel DB:\n{}, 1, {}'
        bookmark_html = '## For Bookmark File:\n<li><a href="file://{2}/Documents/Test/Novels/html/kakuyomu_{0}.html">{1} (id:{0})</a>({3})'
        print(info_text.format(work_id, novel_title))
        print(bookmark_html.format(work_id, novel_title, home_dir, novel_auther))

        # 出力先ディレクトリが存在しなければ自動作成する
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:

            print(html_head, file=f)
            print(f"<h2> {novel_title} (id:{work_id}) </h2>", file=f)
            print(f"<h2> by <a href=\"{auther_url}\">{novel_auther}</a>", file=f)
            print(f" ( 最終更新日：{latest_date} ) </h2>", file=f)

            # チャプター有り無し判定により出力内容を変更する
            has_chapter = any(k.startswith("Chapter:") for k in rec01)

            if has_chapter:
                get_chapter_title(f, rec01_data, target_work_id, base_url)
            else:
                get_episode_info(f, rec01_data, target_work_id, base_url)

            print(html_footer, file=f)

    else:
        print(f"【更新なし】コンテンツに変更はありませんでした (最終更新: {latest_date})。HTMLの出力処理をスキップします。")


main()


