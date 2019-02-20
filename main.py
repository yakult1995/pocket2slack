#!/usr/bin/env python
# coding: utf-8

import requests
import os
import json
from datetime import datetime
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

# MySQL接続
mysql_info = 'mysql+pymysql://' + os.environ['MYSQL_USER'] + ':' + os.environ['MYSQL_PASSWORD'] + '@' + os.environ['MYSQL_HOST'] + '/' + os.environ['MYSQL_DATABASE'] + '?charset=utf8'
engine = create_engine(mysql_info, echo=True)


# 内容生成
def make_message(article):
    message_content = article['resolved_title'] + ' -> ' + article['resolved_url']
    return message_content


# SlackにPOSTする内容をセット
def upload_message(text, SLACK_ROOM, SLACK_URL):
    payload_dic = {
        'text': text,
        'channel': SLACK_ROOM,
        'username': 'Pocket',
        'icon_emoji': 'icon'
    }

    # SlackにPOST
    r = requests.post(SLACK_URL, data=json.dumps(payload_dic))

# API用のAttachment
def make_attachement(article):
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
        "footer": "データ取得日次: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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


### Pocketのリスト取得
payload = {'consumer_key': os.environ['CONSUMER_KEY'],
               'access_token': os.environ['ACCESS_TOKEN'],
               'state': 'unread'
               }
r = requests.post('https://getpocket.com/v3/get', data=payload)
articles = r.json()['list']


### MySQLとデータの整合性
rows = engine.execute('SELECT * FROM article')
for row in rows:
    print(row.article_id)

# PocketのIDだけをリスト化
pocket_id_list = []
for index in articles:
    pocket_id_list.append(int(index))

# MySQLからデータ取得
rows = engine.execute('SELECT * FROM article')
database_id_list = []
for row in rows:
    database_id_list.append(row.article_id)

# リストの引き算
diff_id_list = list(set(pocket_id_list) - set(database_id_list))

# 差分の記事を投稿
for id in diff_id_list:
    # リストにあるものをDATABASEに登録
    ins = "INSERT INTO article (article_id, article_url, article_title) VALUES (%s, %s, %s)"
    engine.execute(ins, id, articles[str(id)]['resolved_url'], articles[str(id)]['resolved_title'])
    upload_message_by_api(make_attachement(articles[str(id)]))


for index in articles:
    print(index, articles[index]['resolved_title'], articles[index]['resolved_url'])
