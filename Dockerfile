FROM python:3.6.1

MAINTAINER Karl J. Overå

ADD . /bot
WORKDIR /bot
RUN python setup.py install
EXPOSE 80

CMD run_haikubot.py