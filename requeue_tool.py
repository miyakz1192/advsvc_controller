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

def main():
    descstr = 'DB Operation Tool for advsvc'
    parser = argparse.ArgumentParser(description=descstr)
    
    # ロングオプション
    parser.add_argument('--recid', type=int, help='record id')

    args = parser.parse_args()

    if(args.recid is None):
        print("ERROR: specify record id")
        return

    print("INFO: requeue target")
    session = dbquery.create_session()
    r = dbquery.find_one_by_id(DialogRecord, args.recid)

    if r is None:
        print(f"INFO: record is not found {id}")
        return

    # 結果の表示
    print(r.id, r.status, r.audio2text, r.text2advice)
    if(r.status == DialogRecord.Status.TEXT2ADVICE_START):
        temp_uuid = r.uuid
        temp_in_text = r.audio2text
    session.close()

    # transform rec
    rec2 = Text2AdviceRecord(temp_uuid, temp_in_text, "")
    rec2.timestamp = datetime.datetime.today()

    Text2AdviceServiceReqMessaging().connect_and_basic_publish_record(rec2)
    print("INFO: End")

main()
