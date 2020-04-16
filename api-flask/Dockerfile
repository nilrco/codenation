FROM python:3.7-slim

COPY ./requeriments.txt /requeriments.txt

RUN pip install -r requeriments.txt

RUN mkdir /statsapi

COPY ./app.py /app.py
COPY ./statsapi/data_store.py statsapi/data_store.py
COPY ./statsapi/operation.py statsapi/operation.py

EXPOSE 5000

CMD python3 app.py
