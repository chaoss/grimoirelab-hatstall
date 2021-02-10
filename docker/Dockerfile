# Copyright (C) 2018-2021 Bitergia
# GPLv3 License

FROM debian:buster-slim
MAINTAINER Santiago Dueñas <sduenas@bitergia.com>

ENV DEBIAN_FRONTEND noninteractive
ENV DEPLOY_USER grimoirelab
ENV DEPLOY_USER_DIR /home/${DEPLOY_USER}

# Initial user
RUN useradd ${DEPLOY_USER} --create-home --shell /bin/bash

# install dependencies
RUN apt-get update && \
    apt-get -y install --no-install-recommends \
        bash locales \
        gcc \
        git git-core \
        mariadb-client \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        unzip curl wget sudo ssh vim \
        apache2 libapache2-mod-wsgi-py3 ssl-cert \
        && \
    apt-get clean && \
    find /var/lib/apt/lists -type f -delete

RUN echo "${DEPLOY_USER} ALL=NOPASSWD: ALL" >> /etc/sudoers

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    echo 'LANG="en_US.UTF-8"'>/etc/default/locale && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
ENV LANG C.UTF-8

ADD stage ${DEPLOY_USER_DIR}/stage
RUN chmod 755 ${DEPLOY_USER_DIR}/stage

USER ${DEPLOY_USER}
WORKDIR ${DEPLOY_USER_DIR}

# Install hatstall and dependencies
RUN git clone https://github.com/chaoss/grimoirelab-hatstall.git
RUN sudo pip3 install -r grimoirelab-hatstall/requirements.txt

CMD ${DEPLOY_USER_DIR}/stage
