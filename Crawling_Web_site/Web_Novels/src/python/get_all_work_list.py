import os
import sys
import subprocess
import sqlite3
import argparse

# ==========================================
# === 設定 ===
# ==========================================
LIST_DIR = "../../novel_database/"
DB_FILE_PATH = os.path.join(LIST_DIR, "all_novels_database_01.db")

# CSVモード時に読み込むリストの定義
CSV_TARGETS = {
    "narou": os.path.join(LIST_DIR, "sample_narou_db_01.csv"),
    "kakuyomu": os.path.join(LIST_DIR, "sample_kakuyomu_db_01.csv")
}

## CSV_TARGETS = {
##     "narou": os.path.join(LIST_DIR, "narou_all_novel_id.list"),
##     "kakuyomu": os.path.join(LIST_DIR, "kakuyomu_all_novel_id.list")
## }

# 呼び出すスクリプトの定義
SCRIPTS = {
    "narou": "get_narou_TableOfContents.py",
    "kakuyomu": "get_kakuyomu_TableOfContents.py"
}
# ==========================================


def get_targets_from_sqlite():
    """SQLiteから実行対象(flag=1)の全サイトのリストを取得する"""
    if not os.path.exists(DB_FILE_PATH):
        print(f"エラー: データベースファイルが見つかりません ({DB_FILE_PATH})")
        return []

    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    
    try:
        # サイトに関わらず、flagが1のものを全て取得
        cursor.execute('SELECT novel_id, site_type, title FROM novels WHERE flag = 1')
        rows = cursor.fetchall()
        return rows
    except sqlite3.OperationalError:
        print("エラー: テーブルが存在しません。")
        return []
    finally:
        conn.close()


def get_targets_from_csv():
    """なろうとカクヨムの両方のCSVから実行対象(flag=1)のリストを取得する"""
    targets = []
    
    for site_type, csv_path in CSV_TARGETS.items():
        if not os.path.exists(csv_path):
            print(f"警告: リストファイルが見つかりません ({csv_path})")
            continue

        with open(csv_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split(',', 2)
                if len(parts) >= 3:
                    novel_id = parts[0].strip()
                    flag = parts[1].strip()
                    title = parts[2].strip()
                    
                    if flag == "1":
                        # SQLiteの戻り値と合わせる: (novel_id, site_type, title)
                        targets.append((novel_id, site_type, title))
                    else:
                        print(f"PASS: [{site_type}] {title}")
                        
    return targets


def main():
    # バッチ自体のコマンドライン引数を設定
    parser = argparse.ArgumentParser(description="統合一括スクレイピングバッチ")
    parser.add_argument("--mode", choices=["sqlite", "csv"], default="sqlite", 
                        help="一括処理の管理形式 (デフォルト: sqlite)")
    args = parser.parse_args()
    
    run_mode = args.mode

    print(f"=== 統合一括取得バッチ開始 (モード: {run_mode}) ===")

    # 1. ターゲットの取得
    if run_mode == "sqlite":
        targets = get_targets_from_sqlite()
    else:
        targets = get_targets_from_csv()

    if not targets:
        print("実行対象のコンテンツがありませんでした。")
        sys.exit(0)

    # 2. ターゲットの実行ループ
    for novel_id, site_type, title in targets:
        print(f"\n==========================================")
        print(f"処理開始: [{site_type}] {title} (ID: {novel_id})")
        print(f"==========================================")
        
        target_script = SCRIPTS.get(site_type)
        if not target_script or not os.path.exists(target_script):
            print(f"エラー: 対応するスクリプトが見つからないか未定義です ({site_type})")
            continue
        
        # 個別スクリプトに novel_id と --mode 引数を渡して実行
        subprocess.run([sys.executable, target_script, novel_id, "--mode", run_mode])

    print("\n=== 統合一括取得バッチ完了 ===")

    # ▼ 追加: バッチ処理後にブックマークを自動生成する
    print("\n=== ブックマークの再生成 ===")
    subprocess.run([sys.executable, "generate_w3m_bookmarks.py"])


if __name__ == "__main__":
    main()

