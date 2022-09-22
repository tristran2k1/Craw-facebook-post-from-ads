FROM mcr.microsoft.com/playwright/python:v1.25.0-focal

WORKDIR /
RUN mkdir -p airflow/xcom 

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

CMD [ "python", "./main.py"]