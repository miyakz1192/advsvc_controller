#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

sleep_sec = 10

while True:
    print("TRACE: work one")

    rec1 = Audio2TextServiceResMessaging().connect_and_basic_get_record()
    if rec1 is None:
        print("TRACE: no data in queue skip this operation. goto next")
        time.sleep(sleep_sec)
        continue

    dr = dbquery.find_one_by(DialogRecord, {"uuid": rec1.id})
    session = dbquery.create_session()
    temp_uuid = dr.uuid
    temp_in_text = rec1.audio2text
    print(f"TRACE: dr.audio2text={dr.audio2text}")
    params = {"status": DialogRecord.Status.TEXT2ADVICE_START,
              "audio2text": rec1.audio2text}
    dbquery.update_one_by_id(tgtcls=DialogRecord, ident=dr. id, params=params)
    session.commit()
    session.close()

    # transform rec
    rec2 = Text2AdviceRecord(temp_uuid, temp_in_text, "")
    rec2.timestamp = datetime.datetime.today()

    Text2AdviceServiceReqMessaging().connect_and_basic_publish_record(rec2)

    # transform rec
    time.sleep(sleep_sec)
