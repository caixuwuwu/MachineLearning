FROM machine-learning-base

WORKDIR /usr/src/app
ADD . /usr/src/app
RUN thrift --gen py eta.thrift
# Expose Port Needed for Thrift-Server
EXPOSE 9001
# Create Entrypoint and default command
ADD entrypoint.sh /usr/local/bin/
# Give execution rights to entrypoint script
RUN chmod 0744 /usr/local/bin/entrypoint.sh
VOLUME /usr/src/app/pickles
ENTRYPOINT [ "entrypoint.sh" ]
CMD [ "up" ]