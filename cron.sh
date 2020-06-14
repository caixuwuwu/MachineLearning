#!/bin/sh

ACTION=$1
echo ACTION=$ACTION

ROOT=/usr/src/app
PY_SCRIPT=/usr/local/bin/python

function act_collect() {
    $PY_SCRIPT collect2.py 2>&1
}

function act_preprocess() {
    for i in quote accept showup work delivery
    do
        echo "starting preprocess.py xgb ${i}"
        $PY_SCRIPT preprocess.py xgb ${i} 2>&1
        echo "preprocess end. sleep 10..."
        sleep 10
    done
}

function act_process() {
    for i in quote accept showup work delivery
    do
        echo "starting process.py xgb ${i} -w "
        $PY_SCRIPT process.py xgb ${i} -w 2>&1
        echo "process end. sleep 3..."
        sleep 3
    done
}

function act_all() {
    act_collect
    act_process
    act_preprocess
}

cd $ROOT

act_${ACTION}
