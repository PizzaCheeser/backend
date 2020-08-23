
FROM python:3.6-buster

COPY requirements.txt /opt/bin/backend/requirements.txt

WORKDIR /opt/bin/backend

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


RUN apt-get update
RUN apt-get install -y software-properties-common
RUN wget -O - http://download.sgjp.pl/apt/sgjp.gpg.key|apt-key add -
RUN echo "deb http://download.sgjp.pl/apt/ubuntu bionic main" >> /etc/apt/sources.list 
RUN apt-get update
RUN apt-get install -y morfeusz2

COPY lib/morfeusz2-1.9.16-cp36-cp36m-linux_x86_64.whl /opt/bin/backend/morfeusz2-1.9.16-cp36-cp36m-linux_x86_64.whl
RUN pip install morfeusz2-1.9.16-cp36-cp36m-linux_x86_64.whl
RUN rm /opt/bin/backend/morfeusz2-1.9.16-cp36-cp36m-linux_x86_64.whl

COPY ./src /opt/bin/backend/src/
ENV FLASK_APP app.py
ENV FLASK_ENV development
ENV PYTHONPATH /opt/bin/backend/src

WORKDIR /opt/bin/backend/src

CMD ["python3", "main.py"]

