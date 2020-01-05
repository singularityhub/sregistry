FROM python:3.5.7-slim-buster
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive
ENV MESSAGELEVEL QUIET

ARG ENABLE_REMOTEBUILD=true

################################################################################
# CORE
# Do not modify this section

RUN apt-get update && apt-get install -y \
    net-tools \
    build-essential \
    libssl-dev \
    uuid-dev \
    libgpgme11-dev \
    squashfs-tools \
    libseccomp-dev \
    wget \
    pkg-config \
    git \
    cryptsetup \
    debootstrap \
    yum

# Install websocket requisite for remote build
RUN export VERSION=1.13.4 OS=linux ARCH=amd64 && \
  wget https://dl.google.com/go/go$VERSION.$OS-$ARCH.tar.gz && \
  tar -C /usr/local -xzvf go$VERSION.$OS-$ARCH.tar.gz && \
  rm go$VERSION.$OS-$ARCH.tar.gz; \
export VERSION=3.5.1 && \
    wget https://github.com/sylabs/singularity/releases/download/v${VERSION}/singularity-${VERSION}.tar.gz && \
    tar -xzf singularity-${VERSION}.tar.gz -C /tmp && \
        rm singularity-${VERSION}.tar.gz; \
cd /tmp/singularity && export  PATH=/usr/local/go/bin:$PATH && ./mconfig && \
    make -C builddir && \
    make -C builddir install

RUN pip install --upgrade pip
RUN pip install django==2.2.8 djangorestframework==3.10.3 channels channels_redis 

ADD . /code/

WORKDIR /code

RUN apt-get autoremove -y
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

EXPOSE 3032
