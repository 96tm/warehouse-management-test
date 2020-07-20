FROM python:3.8-alpine

RUN mkdir /home/warehouse

WORKDIR /home/warehouse

COPY actionlog actionlog
COPY cargo cargo
COPY category category
COPY common common
COPY customer customer
COPY mainpage mainpage
COPY shipment shipment
COPY supplier supplier
COPY templates templates
COPY warehouse warehouse
COPY warehouse-management-test warehouse-management-test
COPY requirements.txt ./
COPY boot.sh ./
COPY manage.py ./

RUN apk update && apk add --no-cache gcc musl-dev jpeg-dev zlib-dev

RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

RUN chmod a+x boot.sh

ENTRYPOINT ["./boot.sh"]
