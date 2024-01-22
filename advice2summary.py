#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
指定した日付を入力するとその日の週のレコードデータのアドバイスの要約を行う。
1) 指定した日付から、レコード群を抽出する
2) レコード群のadviceテキストをpublishする
   advice2summaryサービス側ではadviceテキストの配列を"###"で連結しないと行けない
   ※　rabbit mqに入力可能なデータサイズのチューニングなどに注意!
3) advice2summary_dbサービスを作っておいて、getをループして待つ（データに保存せずにとりあえず画面表示くらいまで)
"""

import sys
import uuid
import time
import argparse

# setting of import messaging
sys.path.append("messaging")
sys.path.append("db")
from messaging import *
from record import *
import dbinitializer
import dbquery
from dbmodels import *

descstr = "sample"
parser = argparse.ArgumentParser(description=descstr)

parser.add_argument('year', type=int)
parser.add_argument('month', type=int)
parser.add_argument('day', type=int)

args = parser.parse_args()

engine = dbinitializer.create_engine()
dbquery.init_and_connect(engine)

advice_texts = []
for r in dbquery.find_by_day(DialogRecord, args.year, args.month, args.day):
    a2t = r.audio2text[:30].replace("\n","")
    print(f"{r.id},{r.timestamp},{a2t}")
    advice_texts.append(r.audio2text)

rec = Advice2SummaryRecord(ident=None,
                           advice_texts=advice_texts,
                           summary_text=None)

Advice2SummaryServiceReqMessaging().connect_and_basic_publish_record(rec)
# rec = Advice2SummaryServiceReqMessaging().connect_and_basic_get_record()
# print(len(rec.advice_texts))
