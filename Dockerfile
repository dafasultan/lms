FROM python:3.12

ENV PYTHONUNBUFFERED=1

WORKDIR /code/
COPY ./code /code

RUN pip install -r /code/requirements.txt
