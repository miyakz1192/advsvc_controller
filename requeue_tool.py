#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import uuid
import time
import datetime

# setting of import messaging
sys.path.append("messaging")
sys.path.append("db")
from messaging import *
import dbinitializer
import dbquery
from dbmodels import *

engine = dbinitializer.create_engine()
dbquery.init_and_connect(engine)

def requeue_text2advice(recid):
    print("INFO: requeue target")
    session = dbquery.create_session()
    r = dbquery.find_one_by_id(DialogRecord, recid)

    if r is None:
        print(f"INFO: record is not found {id}")
        return

    # 結果の表示
    print(r.id, r.status, r.audio2text, r.text2advice)
    temp_uuid = r.uuid
    temp_in_text = r.audio2text
    session.close()

    # transform rec
    rec2 = Text2AdviceRecord(temp_uuid, temp_in_text, "", "")
    rec2.timestamp = datetime.datetime.today()

    Text2AdviceServiceReqMessaging().connect_and_basic_publish_record(rec2)
    print("INFO: End")


def requeue_advice2summary(recid):
    print("INFO: requeue target(advice2summary)")
    session = dbquery.create_session()
    r = dbquery.find_one_by_id(SummaryRecord, recid)

    if r is None:
        print(f"INFO: record is not found {id}")
        return

    # 結果の表示
    print(r.id, r.advice2summary, r.timestamp)
    temp_uuid = r.uuid

    advice_texts = []
    year = r.timestamp.year
    month = r.timestamp.month
    day = r.timestamp.day
    for r in dbquery.find_by_day(DialogRecord, year, month, day):
        t2a = None
        if r.text2advice is not None:
            t2a = r.text2advice[:30].replace("\n","")
        print(f"{r.id},{r.timestamp},{t2a}")
        advice_texts.append(r.text2advice)
    session.close()

    rec = Advice2SummaryRecord(ident=temp_uuid,
                               advice_texts=advice_texts,
                               summary_text=None)
    
    Advice2SummaryServiceReqMessaging().connect_and_basic_publish_record(rec)
    print("INFO: End(advice2summary)")


def requeue_record(wav):
    with open(wav, 'rb') as file:
        # ファイルから全体のバイトデータを読み込む
        binary_data = file.read()

    rec = RawAudioRecord(binary_data)
    RecoderServiceMessaging().connect_and_basic_publish_record(rec)

    print("INFO: End")

def main():
    descstr = 'DB Operation Tool for advsvc'
    parser = argparse.ArgumentParser(description=descstr)
    
    # ロングオプション
    parser.add_argument('--recid', type=int, help='record id(text2advice)')
    parser.add_argument('--recida2s', type=int, help='record id(advice2summary)')
    parser.add_argument('--wav', type=str, help='wav file to record')

    args = parser.parse_args()

    if args.recid is not None:
        print("INFO: text2advice")
        requeue_text2advice(args.recid)
        return

    if args.recida2s is not None:
        print("INFO: advice2summary")
        requeue_advice2summary(args.recida2s)
        return

    if args.wav is not None:
        print("INFO: record")
        requeue_record(args.wav)
        return


main()
