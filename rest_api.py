#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json

from flask import Flask
from flask import make_response

# setting of import messaging
sys.path.append("messaging")
sys.path.append("db")
from messaging import *
from record import *
import dbinitializer
import dbquery
from dbmodels import *

app = Flask(__name__)

def get_record_with_ymd(cls, callback, year, month, day):
    engine = dbinitializer.create_engine()
    dbquery.init_and_connect(engine)
    res = [] 
    for r in dbquery.find_by_day(cls, year, month, day):
        rj = callback(r)

        # ensure_ascii=Falseを指定しないと、JSONの中身のデータが日本語にならずに、
        # unicode escapeされたascii文字列になる
        res.append(rj)

    ret = json.dumps(res, ensure_ascii=False)
    return make_response(ret)

def callback_DialogRecord(record):
    rj = { "audio2text": record.audio2text,
           "text2advice": record.text2advice,}
    return rj


def callback_SummaryRecord(record):
    rj = { "advice2summary": record.advice2summary}
    return rj


@app.route("/dialogs/<int:year>/<int:month>/<int:day>/")
def get_dialogs(year, month, day):
    return get_record_with_ymd(DialogRecord,
                               callback_DialogRecord,
                               year, month, day)


@app.route("/summaries/<int:year>/<int:month>/<int:day>/")
def get_summaries(year, month, day):
    return get_record_with_ymd(SummaryRecord,
                               callback_SummaryRecord,
                               year, month, day)


app.run(host="0.0.0.0", port=8080, debug=True)

#if __name__ == "__main__":
#    app.run(host="0.0.0.0", port=8080, debug=True)
