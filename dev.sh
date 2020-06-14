#!/bin/sh
CMD=${1-up}
echo "Command: $CMD"
if [ "$CMD" == 'build' ]; then
    docker-compose -f Docker/docker-compose-build.yml up build-kinming-eta build-base
    docker-compose -f Docker/docker-compose-build.yml down
elif [ "$CMD" == 'rebuild' ]; then
    ./dev.sh down
    [ ! -z $(docker images -q kinming_eta) ] && docker rmi $(docker images | grep "kinming_eta" | awk '{print $3}')
    ./dev.sh build
elif [ "$CMD" == 'down' ]; then
    docker-compose -f Docker/docker-compose.yml down
elif [ "$CMD" == 'up' ]; then
    docker-compose -f Docker/docker-compose.yml up
elif [ "$CMD" == 'unittest' ]; then
    docker-compose -f Docker/docker-compose-ut.yml up
    docker-compose -f Docker/docker-compose-ut.yml down
elif [ "$CMD" == 'clear' ]; then
    if [ ! -z $(docker ps -a -q -f name=kinming_eta*) ]; then
        docker-compose -f Docker/docker-compose-build.yml down
        docker-compose -f Docker/docker-compose.yml down
        docker stop $(docker ps -a -q -f name=kinming_eta*)
        docker rm $(docker ps -a -q -f name=kinming_eta*)
    fi
    if [ ! -z $(docker images -q kinming_eta) ]; then
        docker rmi kinming_eta
    fi
    if [ ! -z $(docker images -q kinming_eta_xgb) ]; then
        docker rmi kinming_eta_xgb
    fi
    if [ ! -z $(docker images -q kinming_eta_base) ]; then
        docker rmi kinming_eta_base
    fi
    if [ ! -z $(docker images -q registry.cn-hongkong.aliyuncs.com/kinming/machine-learning) ]; then
        docker rmi registry.registry.cn-hongkong.aliyuncs.com/kinming/machine-learning
    fi
elif [ "$CMD" == 'deploy' ]; then
    TAG=$2
    if [ "$TAG" == '' ]; then
        echo "empty tag!"
    else
        echo "tag: $TAG"
        git tag -d $TAG
        git tag $TAG
        git push origin $TAG
    fi
fi
