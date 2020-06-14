#!/bin/sh
CMD="${1}"
shift
PARAM="$@"
echo "Entrypoint: $CMD $PARAM"
echo "Cron: $CONFIGS_CRON"

PICKLE_PREFIX=""
if [ "$ENV_PICKLE_PREFIX" != "" ]; then
    PICKLE_PREFIX="${ENV_PICKLE_PREFIX}-"
else
    if [ "$APP_MODE" != "release" ]; then
        PICKLE_PREFIX="$APP_MODE-$ZONE-"
    fi
fi

function start_cron() {
    if [ "$CONFIGS_CRON" != "" ]; then
        cp configs/$CONFIGS_CRON /etc/crontabs/eta_cron
    else
        cp configs/${ZONE}-cron /etc/crontabs/eta_cron
    fi
    chmod 0644 /etc/crontabs/eta_cron
    echo "Installing Crontab at $(date)"
    cat /etc/crontabs/eta_cron
    if [ "$APP_MODE" != "local" ]; then
        echo
        crontab /etc/crontabs/eta_cron && crond -f -S &
    else
        echo "In the local env, you need to manully run: crontab /etc/crontabs/eta_cron && crond -f -S &"
    fi
}

function collect_data() {
    echo "Launch initial Data-Collection-2 at $(date)"
    if [ "$PARAM" != "" ]; then
        echo "Data-Collection up to $PARAM"
        python collect.py -d "$PARAM"
    else
        echo "Data-Collection up to $(date)"
        python collect.py
    fi

    echo "Launch initial Data-Collection-1 at $(date)"
    if [ "$PARAM" != "" ]; then
        echo "Data-Collection up to $PARAM"
        python collect.py -d "$PARAM"
    else
        echo "Data-Collection up to $(date)"
        python collect.py
    fi
}

function create_pkl() {
## If no random_forest accept pickle exist, run preprocess random_forest accept
    if [ ! -e /usr/src/app/pickles/${PICKLE_PREFIX}xgb_accept.pkl ]; then
        echo "Launch Accept-Duration Preprocess at $(date)"
        if [ -n $PARAM ]; then
            echo "Preprocess and Fit Accept-Duration on date $PARAM"
            python preprocess.py xgb accept -d "$PARAM"
        else
            echo "Proprocess and Fit Accept-Duration on date $(date)"
            python preprocess.py xgb accept
        fi
    else
        echo 'Previous Accept-Duration Model exists!'
    fi

    sleep 5



if [ "${CMD}" == 'up' ]; then
    LOG_FILE=logs/${APP_MODE}_${ZONE}_log_kinming_eta_cron.log
    if [ ! -e /usr/src/app/${LOG_FILE} ]; then
        touch /usr/src/app/${LOG_FILE}
    fi

    start_cron;

    collect_data;

    create_pkl;

    ## Remove Cached Machine-Learning Tmp Files defined in JOBLIB_TEMP_FOLDER env var
#    rm -rf /tmp/*

    tail -f $LOG_FILE

elif [ "${CMD}" == 'up-web-only-new' ]; then
    echo "Launch Web Server at $(date)"
    # gunicorn -b 0.0.0.0:8000 -k gevent app_server:app
    GUNICORN_CMD_ARGS="$PARAM" gunicorn app_server:app
elif [ "${CMD}" == 'up-thrift-only' ]; then
    echo "Launch Thrift Server at $(date)"
    # python daemon.py --thrift-only
    python thrift_server.py
# elif [ "${CMD}" == 'up-web-thrift' ]; then
#     echo "Launch Web and Thrift Daemon at $(date)"
#     python daemon.py
elif [ "${CMD}" == 'down' ]; then
    echo "Removing all tasks from Cron at $(date)"
    crontab -r
elif [ "${CMD}" == 'preprocess' ]; then
    echo "Running Preprocess at $(date) with Param: $PARAM"
    exec python preprocess.py $PARAM
# elif [ "${CMD}" == 'daemon' ]; then
#     echo "Launch Web Daemon at $(date)"
#     python daemon.py
elif [ "${CMD}" == 'clear_logs' ]; then
    rm -rf logs/*
elif [ "${CMD}" == 'clear_pickles' ]; then
    rm -rf pickles/*
elif [ "${CMD}" == 'is_built' ]; then
    echo 'Image was built successfully'
elif [ "${CMD}" == 'requirements_reset' ]; then
    echo "Uninstalling pip requirements at $(date)"
    pip uninstall -r requirements.txt -y
    echo "Installing pip requirements at $(date)"
    pip install -r requirements.txt
elif [ "${CMD}" == 'tunnel' ]; then
    echo 'Creating SSH tunnel'
    exec /bin/bash
else
    $CMD $PARAM
fi