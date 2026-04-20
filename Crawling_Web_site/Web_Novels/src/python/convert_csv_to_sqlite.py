import sqlite3
import os
import re

# ==========================================
# === 設定 ===
# ==========================================
LIST_DIR = "../../novel_database/"
DB_FILE_PATH = os.path.join(LIST_DIR, "all_novels_database_01.db") # または sampl_database_01.db

CSV_FILES = {
    "narou": os.path.join(LIST_DIR, "narou_all_novel_id.list"),
    "kakuyomu": os.path.join(LIST_DIR, "kakuyomu_all_novel_id.list")
}
# ==========================================

def init_db(cursor):
    """テーブルが存在しない場合は作成する"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS novels (
            novel_id TEXT PRIMARY KEY,
            site_type TEXT,
            flag INTEGER,
            title TEXT,
            last_update TEXT
        )
    ''')

def parse_csv_line(line):
    """
    CSVの1行をパースし、ID, フラグ, タイトル, 更新日時を抽出する
    対応フォーマット: 
    - [ID], [flag], [title]
    - [ID], [flag], [title], [last_update]
    """
    line = line.strip()
    if not line:
        return None
        
    parts = line.split(',', 2)
    if len(parts) < 3:
        return None
        
    novel_id = parts[0].strip()
    
    # flagのパース (数値変換エラーを防ぐ)
    try:
        flag = int(parts[1].strip())
    except ValueError:
        flag = 1 # 万が一数値でなければ1(対象)とする

    rest = parts[2].strip()
    title = rest
    last_update = ""

    # タイトルの後ろにカンマ区切りで日付がついているかチェック
    sub_parts = rest.rsplit(',', 1)
    if len(sub_parts) == 2:
        date_candidate = sub_parts[1].strip()
        # なろう(YYYY/MM/DD) または カクヨム(YYYY年MM月DD日) の正規表現チェック
        if re.search(r'\d{4}/\d{2}/\d{2}', date_candidate) or re.search(r'\d{4}年\d{2}月\d{2}日', date_candidate):
            title = sub_parts[0].strip()
            last_update = date_candidate

    return novel_id, flag, title, last_update

def main():
    print("=== CSV to SQLite コンバートを開始します ===")
    
    # DBディレクトリの確保
    os.makedirs(os.path.dirname(DB_FILE_PATH), exist_ok=True)
    
    # DB接続と初期化
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    init_db(cursor)

    total_count = 0

    for site_type, csv_path in CSV_FILES.items():
        if not os.path.exists(csv_path):
            print(f"スキップ: リストファイルが見つかりません ({csv_path})")
            continue

        print(f"\n[{site_type}] のリストを読み込み中: {csv_path}")
        count = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            for line in f:
                parsed = parse_csv_line(line)
                if parsed:
                    novel_id, flag, title, last_update = parsed
                    
                    # SQLiteの INSERT OR REPLACE (UPSERT) を使用
                    cursor.execute('''
                        INSERT OR REPLACE INTO novels (novel_id, site_type, flag, title, last_update)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (novel_id, site_type, flag, title, last_update))
                    
                    print(f"  -> 登録/更新: [{novel_id}] {title[:20]}... (フラグ:{flag})")
                    count += 1
                    
        print(f"[{site_type}] の登録完了: {count} 件")
        total_count += count

    # コミットして終了
    conn.commit()
    conn.close()
    
    print(f"\n=== コンバート完了！ 合計 {total_count} 件のデータがDBに登録されました ===")
    print("これで get_all_work_list.py (統合バッチ) がすぐに実行可能です。")

if __name__ == "__main__":
    main()
