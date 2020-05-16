FROM python:3.4

ARG targetBranch=development
ARG originBranch=development
ARG defaultBranch=development
ARG pullRequest=false

ENV DEFAULT_BRANCH=${defaultBranch}
ENV TRAVIS_BRANCH=${targetBranch}
ENV TRAVIS_PULL_REQUEST_BRANCH=${originBranch}
ENV TRAVIS_PULL_REQUEST=${pullRequest}

RUN /bin/echo -e "\e[1;35mORIGIN BRANCH ------------ $originBranch\e[0m" &&\
    /bin/echo -e "\e[1;35mTARGET BRANCH ------------ $targetBranch\e[0m" &&\
    /bin/echo -e "\e[1;35mDEFAULT BRANCH ------------ $defaultBranch\e[0m"

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY copy_.py copy_.py
RUN python copy_.py https://github.com/openworm/geppetto-application.git