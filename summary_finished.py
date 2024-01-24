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

    rec1 = Advice2SummaryServiceResMessaging().connect_and_basic_get_record()
    if rec1 is None:
        print("TRACE: no data in queue skip this operation. goto next")
        time.sleep(sleep_sec)
        continue

    r = dbquery.find_one_by(SummaryRecord, {"uuid": rec1.id})
    session = dbquery.create_session()
    params = {"advice2summary": rec1.summary_text}
    dbquery.update_one_by_id(tgtcls=SummaryRecord, ident=r.id, params=params)
    print(f"TRACE: r.advice2summary{r.advice2summary}")
    session.commit()
    session.close()

    # transform rec
    time.sleep(sleep_sec)
