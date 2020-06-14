FROM machine-learning-model
RUN apk add htop \
    g++
#RUN pip install cython thriftpy && rm -rf ~/.cache/pip
WORKDIR /usr/src/app
ADD . /usr/src/app
RUN thrift --gen py eta.thrift
#RUN mkdir /tmp
# Expose Port Needed for Thrift-Server
EXPOSE 8000 9090
# Create Entrypoint and default command
ADD entrypoint.sh /usr/local/bin/
# Give execution rights to entrypoint script
RUN chmod 0744 /usr/local/bin/entrypoint.sh
VOLUME /usr/src/app/pickles
ENTRYPOINT [ "entrypoint.sh" ]
CMD [ "up" ]