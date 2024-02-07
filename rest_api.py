#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import subprocess

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
from advice2summary import create_advice2summary

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
    response = make_response(ret)
    return (res, response)

def callback_DialogRecord(record):
    rj = { "audio2text": record.audio2text,
           "text2advice": record.text2advice,}
    return rj


def callback_SummaryRecord(record):
    rj = { "advice2summary": record.advice2summary}
    return rj


@app.route("/dialogs/<int:year>/<int:month>/<int:day>/")
def get_dialogs(year, month, day):
    (_, response) = get_record_with_ymd(DialogRecord,
                                       callback_DialogRecord,
                                       year, month, day)
    return response


@app.route("/summaries/<int:year>/<int:month>/<int:day>/")
def get_summaries(year, month, day):
    print("INFO: calling get_summaries")
    # ちょっとわかりにくい実装で気持ち悪いが、
    # getの時にSummaryRecordがなければ、作る要求も出してしまう。
    # TODO: FIXME: PUT/GETでAPIを使い分けた実装にリファクタする。
    (res, response) = get_record_with_ymd(SummaryRecord,
                                          callback_SummaryRecord,
                                          year, month, day)
    print(f"INFO: get records={len(res)}")
    print(res)
    if(len(res) == 0):
        print(f"INFO: calling create_advice2summary")
        create_advice2summary(year, month, day)
    print(f"INFO: end of get_summaries")
    return response


# シェルコマンドを実行し、標準出力を得る
def run_shell_command(shell_command):
    result = subprocess.run(shell_command, shell=True, check=True, stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')


@app.route("/operations/requeue/all/")
def operations_requeue_all():
    res = run_shell_command("bash -c \"cd ~ ; pwd ; ./requeue_ope_advice.sh ; ./requeue_ope_whisper.sh\"")
    return make_response(res)


@app.route("/operations/requeue/advice/")
def operations_requeue_advice():
    res = run_shell_command("bash -c \"cd ~ ; pwd ; ./requeue_ope_advice.sh \"")
    return make_response(res)


@app.route("/operations/requeue/whisper/")
def operations_requeue_whisper():
    res = run_shell_command("bash -c \"cd ~ ; pwd ; ./requeue_ope_whisper.sh\"")
    return make_response(res)


app.run(host="0.0.0.0", port=8080, debug=True)

#if __name__ == "__main__":
#    app.run(host="0.0.0.0", port=8080, debug=True)
