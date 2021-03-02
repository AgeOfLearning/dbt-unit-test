FROM python:3.8
RUN pip install --upgrade pip
COPY ./requirements-dev.txt requirements-dev.txt
COPY ./requirements.txt requirements.txt

RUN pip install -r requirements-dev.txt
RUN pip install -r requirements.txt


