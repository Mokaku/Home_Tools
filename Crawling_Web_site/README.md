# get_xxx_manga_site_pict.py
#####################################

## What's this?
某サイトの画像を取得するためのスクリプト
某サイトにアップされた画像のURLを連続して抽出し、zipで書庫化したあとAWS S3にアップロードします。


## 何のためにあるの？
- BeautifulSoup の練習用です

## How to USE

1. SourceをClone
2. 適当な場所に配置
3. pip で下記の必要なものをインストール
4. 必要に応じて1行目の `#!/usr/bin/python3`のパスを書き換える `#!/usr/bin/python3.6`等
5. ${BASE_DIR}/Home_Tools/Crawling_Web_site 内で ../get_xxx_manga_site_pict.py [Start_page] [End_Page] [コンテンツナンバー] を入力して実行
6. 事前にS3のバケットを準備しておかないといけない（でパスをスクリプト内で変更する必要がある)

## requre
### Python
- python 3.5~

### Python module
- beautifulsoup4==4.4.1
- lxml==4.2.1
- requests==2.9.1
- bota3

`# sudo pip install beautifulsoup4 lxml requests bota3` でインストールしてください

### その他必要なもの
- awscli
データ確認用　まぁAWSのコンソールで見るって手もあるけど。
スクリプトの稼働には必要はない

Ubuntu の場合は
`# sudo apt-get install libxslt1-dev libxml2 python-dev `
の後に
`sudo pip install --upgrade lxml`

としないとlxmlのversionが3.7.xのままで
`bs4.FeatureNotFound: Couldn't find a tree builder with the features you requested: lxml. Do you need to install a parser library`
とか出てハマるので注意

## 余談
データサンプリング元のサイトがブログエンジン利用したエロ漫画のサイトなのでデータが扱いやすい・それなりのボリュームが有る（圧縮処理・データの保存などの処理練習をしたかった。)



