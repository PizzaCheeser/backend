

FROM python:3.7
# We copy just the requirements.txt first to leverage Docker cache 
COPY requirements.txt /opt/bin/backend/requirements.txt

WORKDIR /opt/bin/backend
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./src /opt/bin/backend/src/
ENV FLASK_APP app.py
ENV FLASK_ENV development
ENV PYTHONPATH /opt/bin/backend/src

WORKDIR /opt/bin/backend/src

CMD ["python3", "main.py"]

