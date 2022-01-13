FROM python:3.9-slim-buster

WORKDIR /dontbudge

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . /dontbudge

EXPOSE 9876

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:9876", "run:app"]