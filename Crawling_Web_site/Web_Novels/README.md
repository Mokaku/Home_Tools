# Web Novels Scraper (なろう / カクヨム 一括取得ツール)

小説家になろう（ncode.syosetu.com）および カクヨム（kakuyomu.jp）から小説の目次情報をスクレイピングし、ローカルにHTMLとJSON形式で保存するツール群です。
SQLiteデータベース、またはCSV形式のリストファイルを用いて、**「更新があった作品のみを差分取得する」**スマートな一括処理（バッチ処理）に対応しています。

## 🌟 特徴
- **差分更新対応:** SQLite DBまたはCSVの最終更新日時を比較し、無駄な通信とファイル出力をスキップ。
- **統合バッチ処理:** なろう・カクヨム両方のサイトを1つのコマンドで一括更新。
- **モード切替:** コマンドライン引数 `--mode sqlite` / `--mode csv` で管理形式を柔軟に変更可能。

---

## 🛠 前提条件 (Prerequisites)

このスクリプトをまっさらな環境で実行するためには、以下のツールが必要です。

- **OS:** macOS / Linux / Windows (macOS推奨)
- **Python:** 3.13 以上
- **パッケージマネージャ:** Pipenv

### Mac環境での推奨セットアップ（Homebrewを使用）
まだPython環境がない場合は、`pyenv` と `pipenv` をインストールしてください。
```bash
brew install pyenv pipenv openssl xz
```

---

## 🚀 環境構築手順 (Installation)

### 1. リポジトリの取得
Gitからメインブランチのソースコードをクローンし、対象ディレクトリへ移動します。
```bash
git clone [https://github.com/Mokaku/Home_Tools.git](https://github.com/Mokaku/Home_Tools.git)
cd Home_Tools/Crawling_Web_site/Web_Novels
```

### 2. Pythonのインストールと仮想環境の構築
本プロジェクトは `Pipenv` を使用して依存パッケージ（BeautifulSoup4, requests 等）を管理しています。スクリプトのあるディレクトリ（`Pipfile` がある場所）に移動してセットアップを行います。

```bash
# スクリプトとPipfileがあるディレクトリへ移動
cd src/python

# 依存パッケージのインストール（仮想環境の自動作成）
pipenv install
```

> **⚠️ 【重要】MacでPythonのインストールエラー（SSLモジュールエラー）が出る場合**
> Mac環境で `pipenv install` 時にSSLエラーが出たり、pyenvでのPythonビルドが失敗する場合は、Mac標準のコンパイラとHomebrewのOpenSSLを明示的に指定してPythonをインストールしてください。
> ```bash
> # 1. Command Line Toolsの再インストール（必要な場合のみ）
> sudo rm -rf /Library/Developer/CommandLineTools
> xcode-select --install
> 
> # 2. Apple純正ツールを強制指定してPython 3.13系をインストール
> AR=/usr/bin/ar RANLIB=/usr/bin/ranlib CC=clang LDFLAGS="-L$(brew --prefix openssl@3)/lib" CPPFLAGS="-I$(brew --prefix openssl@3)/include" pyenv install 3.13.2
> 
> # 3. インストールしたバージョンをローカルに適用し、再度Pipenvを実行
> pyenv local 3.13.2
> pipenv install
> ```

---

## 📁 ディレクトリ構成

実行前に、以下のディレクトリ構成になっていることを確認してください（スクリプト実行時に自動生成されるものもあります）。

```text
Web_Novels/
├── html/                  # 生成されたHTML/JSONが出力される場所
├── novel_database/        # DBおよびCSVリストの保存場所
│   ├── kakuyomu_all_novel_id.list
│   ├── narou_all_novel_id.list
│   └── sampl_database_01.db (自動生成)
└── src/
    └── python/            # スクリプト本体
        ├── Pipfile
        ├── get_all_work_list.py             # 統合バッチスクリプト
        ├── get_narou_TableOfContents.py     # なろう個別スクリプト
        └── get_kakuyomu_TableOfContents.py  # カクヨム個別スクリプト
```

---

## 使い方 (Usage)

スクリプトはすべて `src/python/` ディレクトリ内で、`pipenv run` を付けて実行します。

### 1. 統合バッチによる一括取得（推奨）
DB（またはCSV）に登録されている `flag = 1` の全作品を巡回し、更新があったものだけを取得します。

**SQLiteモードで実行（デフォルト）:**
```bash
pipenv run python get_all_work_list.py
```
**CSVモードで実行:**
```bash
pipenv run python get_all_work_list.py --mode csv
```

### 2. 個別作品の手動取得
特定の作品だけをピンポイントで取得・更新したい場合は、個別スクリプトにIDを渡して実行します。
（※初回実行時、自動的にDBまたはCSVに作品情報が登録されます）

**なろうの作品を取得:**
```bash
pipenv run python get_narou_TableOfContents.py n2732lu
```
**カクヨムの作品を取得:**
```bash
pipenv run python get_kakuyomu_TableOfContents.py 16817330667341551839
```

---

## 📝 データベース/リストの仕様

### SQLiteデータベース (`sampl_database_01.db`)
初回実行時に自動作成される `novels` テーブルで管理されます。
- `novel_id` (TEXT): nコード、またはカクヨムの19桁ID
- `site_type` (TEXT): `narou` または `kakuyomu`
- `flag` (INTEGER): `1`=一括処理の対象 / `0`=対象外
- `title` (TEXT): 作品名
- `last_update` (TEXT): 最終更新日時

### CSVリスト (`.list` ファイル)
カンマ区切りで管理されます。手動で追記する場合は以下のフォーマットに従ってください。
`[ID], [取得フラグ(1 or 0)], [タイトル]`

*(例: narou_all_novel_id.list)*
```csv
n2732lu, 1, リナニア戦記　～悪役貴族と転生従士は平和の国の夢を見るか～
n6453iq, 0, 春暁記
```

---

## 🗄️ SQLite 基本操作チートシート

運用中、直接データベースの中身を確認したり、手動でフラグを修正したりするための基本的なコマンドリストです。

### 1. データベースへの接続と終了
ターミナルで以下のコマンドを入力してSQLiteを起動します。
```bash
# データベースファイルを開く (※パスは実行場所に合わせる)
sqlite3 ../../novel_database/sampl_database_01.db
```

SQLiteのプロンプト (`sqlite>`) に入ったら、以下のコマンドが使えます。
```sql
.tables           -- 存在するテーブルの一覧を表示 (novels と出ればOK)
.schema novels    -- テーブルの構造(カラム名や型)を確認
.mode column      -- ★おすすめ: 検索結果を縦に揃えて見やすくする
.headers on       -- ★おすすめ: 検索結果の一番上にカラム名を表示する
.quit             -- SQLiteを終了して元のターミナルに戻る
```

### 2. データの確認 (SELECT)
※SQL文の最後には必ず `;` (セミコロン) をつけてエンターを押します。

**登録されている全データを表示**
```sql
SELECT * FROM novels;
```

**「なろう」の作品だけを絞り込んで表示**
```sql
SELECT novel_id, title, last_update FROM novels WHERE site_type = 'narou';
```

**「バッチ処理の対象 (flag=1)」の作品だけを表示**
```sql
SELECT novel_id, site_type, title FROM novels WHERE flag = 1;
```

### 3. データの更新・変更 (UPDATE)
作品を一括取得の対象外にしたい場合などに使用します。

**特定の作品を一括取得の「対象外 (flag=0)」に変更する**
```sql
UPDATE novels SET flag = 0 WHERE novel_id = 'n2732lu';
```
*(※元に戻すときは `SET flag = 1` にして実行します)*

### 4. データの削除 (DELETE)
不要になった作品をデータベースから完全に消去します。
*(※削除は取り消せないので実行前にIDをよく確認してください)*

**特定の作品を削除する**
```sql
DELETE FROM novels WHERE novel_id = 'n6453iq';
```

