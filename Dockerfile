FROM python:3.9.1

RUN mkdir /service
COPY . /service

RUN cd /service && pip install -r requirements.txt

VOLUME [ "/data" ]
EXPOSE 48986
WORKDIR /service
ENTRYPOINT [ "python", "main.py", "--config=/data/config.json" ]