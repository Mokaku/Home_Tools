import sqlite3
import os
import datetime
import re

# ==========================================
# === 設定 ===
# ==========================================
DB_FILE_PATH = "../../novel_database/all_novels_database_01.db"
BOOKMARK_OUTPUT_PATH = "../../novel_database/bookmark.html"  # 出力先

# HTMLが保存されているベースディレクトリの絶対パスを取得
# 例: /Users/mmiotproject/Documents/Private/Novels/html
BASE_HTML_DIR = os.path.abspath("../../html")

# 何日以内を「更新」とみなすかの設定
NEW_MARK_DAYS = 7
# ==========================================

def parse_last_update(date_str, site_type):
    """サイトごとの日付文字列をdatetimeオブジェクトに変換する"""
    if not date_str:
        return None
        
    # なろう特有の「（改）」などのゴミを削除
    clean_date_str = re.sub(r'（改）$', '', date_str).strip()
    
    try:
        if site_type == "narou":
            # なろう: 2026/04/15 07:00
            return datetime.datetime.strptime(clean_date_str, "%Y/%m/%d %H:%M")
        elif site_type == "kakuyomu":
            # カクヨム: 2026年04月09日 15:00
            return datetime.datetime.strptime(clean_date_str, "%Y年%m月%d日 %H:%M")
    except ValueError:
        return None
        
    return None

def get_novels_from_db():
    """DBから小説データを取得し、サイト別に分類して返す"""
    if not os.path.exists(DB_FILE_PATH):
        print(f"エラー: データベースが見つかりません: {DB_FILE_PATH}")
        return {}
        
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    # site_typeごとに辞書にまとめる
    novels_by_site = {"narou": [], "kakuyomu": []}
    
    try:
        # flagが1（取得対象）のものを取得
        cursor.execute('SELECT novel_id, site_type, title, last_update FROM novels WHERE flag = 1')
        rows = cursor.fetchall()
        
        now = datetime.datetime.now()
        
        for row in rows:
            novel_id, site_type, title, last_update = row
            
            # 日付パースと更新判定
            dt = parse_last_update(last_update, site_type)
            is_new = False
            if dt:
                # 差分が設定日数以内の場合 True
                if (now - dt).days <= NEW_MARK_DAYS:
                    is_new = True
            
            if site_type in novels_by_site:
                novels_by_site[site_type].append({
                    "id": novel_id,
                    "title": title,
                    "is_new": is_new
                })
                
    except sqlite3.OperationalError:
        print("エラー: テーブルの読み込みに失敗しました。")
    finally:
        conn.close()
        
    return novels_by_site

def generate_bookmark_html():
    novels_by_site = get_novels_from_db()
    if not novels_by_site:
        return
        
    print("w3m用ブックマークを生成しています...")
    
    os.makedirs(os.path.dirname(BOOKMARK_OUTPUT_PATH), exist_ok=True)
    
    with open(BOOKMARK_OUTPUT_PATH, 'w', encoding='utf-8') as f:
        # ヘッダー
        f.write("<html><head><title>Bookmarks</title></head>\n")
        f.write("<body>\n")
        f.write("<h1>Bookmarks</h1>\n")
        
        # --- なろうセクション ---
        if novels_by_site.get("narou"):
            f.write("<h2>なろう読み物</h2>\n")
            f.write("<ul>\n")
            for novel in novels_by_site["narou"]:
                prefix = "[更新] " if novel["is_new"] else ""
                # なろうのHTMLファイルパス: html/narou/narou_XXXXX.html
                file_url = f"file://{BASE_HTML_DIR}/narou/narou_{novel['id']}.html"
                f.write(f'<li><a href="{file_url}">{prefix}{novel["title"]}</a>\n')
            f.write("\n")
            f.write("</ul>\n")
            
        # --- カクヨムセクション ---
        if novels_by_site.get("kakuyomu"):
            f.write("<h2>カクヨム読み物</h2>\n")
            f.write("<ul>\n")
            for novel in novels_by_site["kakuyomu"]:
                prefix = "[更新] " if novel["is_new"] else ""
                # カクヨムのHTMLファイルパス: html/kakuyomu_XXXXX.html
                file_url = f"file://{BASE_HTML_DIR}/kakuyomu_{novel['id']}.html"
                f.write(f'<li><a href="{file_url}">{prefix}{novel["title"]}</a>\n')
            f.write("\n")
            f.write("</ul>\n")
            
        # フッター
        f.write("</body>\n</html>\n")
        
    print(f"完了: {BOOKMARK_OUTPUT_PATH} に出力しました。")

if __name__ == "__main__":
    generate_bookmark_html()

