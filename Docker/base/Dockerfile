FROM python:3.7.5-alpine3.8
LABEL mantainer="caixuwu@outlook.com"

## 设置环境变量
ENV THRIFT_VERSION 0.11.0
ENV TIME_ZONE Asia/Hong_Kong

## Download Build Dependencies
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories \
    && apk add --update --no-cache \
    --virtual=.build-dependencies \
    alpine-sdk \
    curl \
    tar \
    tzdata \
    && cp /usr/share/zoneinfo/${TIME_ZONE} /etc/localtime \
    && echo "${TIME_ZONE}" > /etc/timezone \

## Download and Install Thrift
# RUN curl -sSL "http://apache.01link.hk/thrift/$THRIFT_VERSION/thrift-$THRIFT_VERSION.tar.gz" -o thrift.tar.gz \
    && curl -sSL "http://mirrors.tuna.tsinghua.edu.cn/apache/thrift/$THRIFT_VERSION/thrift-$THRIFT_VERSION.tar.gz" -o thrift.tar.gz \
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
    && pip install requests==2.22.0 happybase==1.2.0 redis==3.3.11 python-dateutil==2.8.1 s2sphere==0.2.5 thrift==0.11.0 pymysql==0.8.0 SQLAlchemy arrow==0.12.1 oss2==2.9.0 \
    && rm -rf ~/.cache/pip \
    && apk del .build-dependencies
