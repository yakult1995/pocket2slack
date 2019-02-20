#!/usr/bin/env python
# coding: utf-8

import requests
import os
from datetime import datetime
from os.path import join, dirname
from dotenv import load_dotenv
from sqlalchemy import create_engine

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# MySQL接続
mysql_info = 'mysql+pymysql://' + os.environ['MYSQL_USER'] + ':' + os.environ['MYSQL_PASSWORD'] + '@' + os.environ['MYSQL_HOST'] + '/' + os.environ['MYSQL_DATABASE'] + '?charset=utf8'
engine = create_engine(mysql_info, echo=True)


# API用のAttachment
def make_attachment(article):
    fields = []
    field = {
        'title': article['resolved_title'],
        'value': article['resolved_url'],
        'short': False
    }
    fields.append(field)
# ---------------------------

    attachment = {
        "fallback": "Pocket新規アイテム",
        "color": "#dd0000",
        "fields": fields,
        "footer": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    slack_params = {
        'channel': os.environ['CHANNEL_ID'],
        'attachments': [attachment]
    }
    return slack_params


# APIを通してメッセージ投稿
def upload_message_by_api(attachment):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + os.environ['SLACK_TOKEN']
    }
    req = requests.post(os.environ['SLACK_MESSAGE_POST_URL'], headers=headers, json=attachment)
    try:
        req.raise_for_status()
        print("Message posted..")
        return req.json()
    except requests.RequestException as e:
        print("Request failed: %s", e)


# Pocketのリスト取得
payload = {
    'consumer_key': os.environ['CONSUMER_KEY'],
    'access_token': os.environ['ACCESS_TOKEN'],
    'state': 'unread'
}

r = requests.post('https://getpocket.com/v3/get', data=payload)
articles = r.json()['list']

# PocketのIDだけをリスト化
pocket_id_list = []
for index in articles:
    pocket_id_list.append(int(index))

# MySQLとデータの整合性
rows = engine.execute('SELECT * FROM article')

# MySQLからデータ取得
rows = engine.execute('SELECT * FROM article')
database_id_list = []
for row in rows:
    database_id_list.append(row.article_id)

# リストの引き算
diff_id_list = list(set(pocket_id_list) - set(database_id_list))

# 差分の記事を投稿
ins = "INSERT INTO article (article_id, article_url, article_title) VALUES (%s, %s, %s)"
for target_id in diff_id_list:
    # リストにあるものをDATABASEに登録
    engine.execute(ins, target_id, articles[str(target_id)]['resolved_url'], articles[str(target_id)]['resolved_title'])
    upload_message_by_api(make_attachment(articles[str(target_id)]))
