FROM python:3.8
RUN pip install --upgrade pip
COPY ./dbt_unit_test/requirements-dev.txt requirements-dev.txt
COPY ./dbt_unit_test/requirements.txt requirements.txt

RUN pip install -r requirements-dev.txt
RUN pip install -r requirements.txt


