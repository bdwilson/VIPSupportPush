FROM debian:stretch-slim

RUN mkdir /code
WORKDIR /code

RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-suds python3-websocket python3-urllib3 python3-requests python3-botocore git && \
    pip3 install flask && \
    pip3 install securitas && \
    pip3 install wtforms

ADD . /code/
EXPOSE 5000
CMD [ "python3", "/code/validator_flask.py" ]
