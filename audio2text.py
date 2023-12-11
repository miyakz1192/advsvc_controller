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

    rec1 = RecoderServiceMessaging().connect_and_basic_get_record()
    if rec1 is None:
        print("TRACE: no data in queue skip this operation. goto next")
        time.sleep(sleep_sec)
        continue

    session = dbquery.create_session()
    dr = DialogRecord()
    dr.raw_audio = rec1.raw_audio_byte
    dr.status = DialogRecord.Status.AUDIO2TEXT_START
    # prevent from not bound error. due to session.close before transform rec
    temp_uuid = dr.uuid
    session.add_all([dr])
    session.commit()
    session.close()

    # transform rec
    rec2 = Audio2TextRecord(temp_uuid, rec1.raw_audio_byte, "")
    rec2.timestamp = datetime.datetime.today()

    Audio2TextServiceReqMessaging().connect_and_basic_publish_record(rec2)
    # transform rec
    time.sleep(sleep_sec)
