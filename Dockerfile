FROM python:3.5.2

MAINTAINER Karl J. Overå

ADD . /bot
WORKDIR /bot
RUN pip install -r requirements.txt
EXPOSE 80

CMD python run.py