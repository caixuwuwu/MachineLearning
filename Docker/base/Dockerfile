FROM python:3.7.8-slim
LABEL mantainer="Xuwu Cai <caixuwu@outlook.com>"

## 设置环境变量
ENV THRIFT_VERSION 0.11.0
ENV TIME_ZONE Asia/Hong_Kong

## Download Build Dependencies
RUN apt-get update \
    && apt-get install -y --autoremove --no-install-recommends \
    cmake \
    make \
    g++ \
    htop\
    curl \
    tar \
    tzdata \
    git \
    && apt-get clean \
    && cp /usr/share/zoneinfo/${TIME_ZONE} /etc/localtime \
    && echo "${TIME_ZONE}" > /etc/timezone

## Download and Install Thrift
RUN curl -sSL "http://mirrors.tuna.tsinghua.edu.cn/apache/thrift/$THRIFT_VERSION/thrift-$THRIFT_VERSION.tar.gz" -o thrift.tar.gz \
    && mkdir -p /usr/src/thrift \
    && tar zxf thrift.tar.gz -C /usr/src/thrift --strip-components=1 \
    && rm thrift.tar.gz \
	&& cd /usr/src/thrift \
    && ./configure --with-python \
    && make \
	&& make install \
	&& cd / \
	&& rm -rf /usr/src/thrift \

    && mkdir -p ~/.pip \
    && echo "[global]" > ~/.pip/pip.conf \
    && echo "index-url=http://mirrors.aliyun.com/pypi/simple/" >> ~/.pip/pip.conf \
    && echo "[install]" >> ~/.pip/pip.conf \
    && echo "trusted-host=mirrors.aliyun.com" >> ~/.pip/pip.conf \
    && pip install --upgrade pip \
    && pip install --no-cache-dir  --disable-pip-version-check scikit-learn==0.20.0 pandas==0.25.3 xgboost==0.80 \
    requests==2.22.0 happybase==1.2.0 redis==3.3.11 python-dateutil==2.8.1 s2sphere==0.2.5 thrift==0.11.0 oss2==2.9.0 \
    pymysql==0.8.0 SQLAlchemy arrow==0.12.1 tensorflow==2.2.0 tensorflowonspark ConcurrentLogHandler==0.9.1 \
    && rm -rf ~/.cache/pip

## Download and Install xgboost
RUN cd /usr/src && \
    git clone --recursive -b v0.81 https://github.com/dmlc/xgboost && \
    sed -i '/#define DMLC_LOG_STACK_TRACE 1/d' /usr/src/xgboost/dmlc-core/include/dmlc/base.h && \
    sed -i '/#define DMLC_LOG_STACK_TRACE 1/d' /usr/src/xgboost/rabit/include/dmlc/base.h

RUN ln -s locale.h /usr/include/xlocale.h && \
    cd /usr/src/xgboost; make -j4 && \
    cd /usr/src/xgboost/python-package && \
    python3 setup.py install && \
    rm /usr/include/xlocale.h && \
    rm -rf /usr/src/xgboost

## Download and Install LightGBM
ENV CC gcc
ENV CXX g++ 
RUN cd /usr/src \
    && git clone --recursive https://github.com/Microsoft/LightGBM \
    && cd /usr/src/LightGBM \
    && mkdir build; cd build \
    && cmake .. \
    && make -j4 \
    && cd /usr/src/LightGBM/python-package; python setup.py install \
    && rm -r /root/.cache \
    && rm -rf /usr/src/LightGBM
