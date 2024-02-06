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
from datetime import datetime



def create_advice2summary(year, month, day):
    engine = dbinitializer.create_engine()
    dbquery.init_and_connect(engine)
    
    advice_texts = []
    for r in dbquery.find_by_day(DialogRecord, year, month, day):
        t2a = None
        if r.text2advice is not None:
            t2a = r.text2advice[:30].replace("\n","")
        print(f"{r.id},{r.timestamp},{t2a}")
        advice_texts.append(r.text2advice)
    
    session = dbquery.create_session()
    sr = SummaryRecord()
    sr.timestamp = datetime(year=year, month=month, day=day)
    temp_uuid = sr.uuid
    session.add_all([sr])
    session.commit()
    session.close()
    
    rec = Advice2SummaryRecord(ident=temp_uuid,
                               advice_texts=advice_texts,
                               summary_text=None)
    
    Advice2SummaryServiceReqMessaging().connect_and_basic_publish_record(rec)
# rec = Advice2SummaryServiceReqMessaging().connect_and_basic_get_record()
# print(len(rec.advice_texts))

if __name__ == "__main__":
    descstr = "sample"
    parser = argparse.ArgumentParser(description=descstr)
    
    parser.add_argument('year', type=int)
    parser.add_argument('month', type=int)
    parser.add_argument('day', type=int)
    
    args = parser.parse_args()

    create_advice2summary(args.year, args.month, args.day)
