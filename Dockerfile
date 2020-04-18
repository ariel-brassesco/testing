FROM python:3.4

ENV DEFAULT_BRANCH='development'
ENV TRAVIS_BRANCH='development'
ENV TRAVIS_PULL_REQUEST_BRANCH='feature/621'
ENV TRAVIS_PULL_REQUEST=1253615151

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY copy_.py copy_.py
RUN python copy_.py http://github.com/openworm/org.geppetto.git