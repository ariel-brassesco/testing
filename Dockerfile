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

RUN python copy_.py https://github.com/ariel-brassesco/testing.git
RUN test -d "testing" && echo -e "\e[1;32mtesting exists.\e[0m" \
    || echo -e "\e[1;31mtesting NOT EXISTS.\e[0m"

# geppetto repos
RUN python copy_.py https://github.com/openworm/org.geppetto.git
RUN test -d "org.geppetto" && echo -e "\e[1;32morg.geppetto exists.\e[0m" \
    || echo -e "\e[1;31mtesting NOT EXISTS.\e[0m"

RUN python copy_.py https://github.com/openworm/org.geppetto.model.git
RUN test -d "org.geppetto.model" && echo -e "\e[1;32morg.geppetto.model exists.\e[0m" \
    || echo -e "\e[1;31morg.geppetto.model NOT EXISTS.\e[0m"

RUN python copy_.py https://github.com/openworm/org.geppetto.core.git
RUN test -d "org.geppetto.core" && echo -e "\e[1;32morg.geppetto.core exists.\e[0m" \
    || echo -e "\e[1;31morg.geppetto.core NOT EXISTS.\e[0m"

RUN python copy_.py https://github.com/openworm/org.geppetto.model.neuroml.git
RUN test -d "org.geppetto.model.neuroml" && echo -e "\e[1;32morg.geppetto.model.neuroml exists.\e[0m" \
    || echo -e "\e[1;31morg.geppetto.model.neuroml NOT EXISTS.\e[0m"

RUN python copy_.py https://github.com/openworm/org.geppetto.simulation.git
RUN test -d "org.geppetto.simulation" && echo -e "\e[1;32morg.geppetto.simulation exists.\e[0m" \
    || echo -e "\e[1;31morg.geppetto.simulation NOT EXISTS.\e[0m"

RUN python copy_.py https://github.com/openworm/org.geppetto.frontend.git
RUN test -d "org.geppetto.frontend" && echo -e "\e[1;32morg.geppetto.frontend exists.\e[0m" \
    || echo -e "\e[1;31morg.geppetto.frontend NOT EXISTS.\e[0m"

RUN python copy_.py https://github.com/openworm/geppetto-application.git
RUN test -d "geppetto-application" && echo -e "\e[1;32mgeppetto-application exists.\e[0m" \
    || echo -e "\e[1;31mgeppetto-application NOT EXISTS.\e[0m"