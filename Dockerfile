FROM python:3.4

ENV DEFAULT_BRANCH='development'
ENV TRAVIS_BRANCH='development'
ENV TRAVIS_PULL_REQUEST_BRANCH='geppetto-client/feature/110'
ENV TRAVIS_PULL_REQUEST=1253615151

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY copy_.py copy_.py
RUN python copy_.py https://github.com/openworm/geppetto-application.git --push