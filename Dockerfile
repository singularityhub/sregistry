FROM python:3.5.7
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive
ENV MESSAGELEVEL QUIET

################################################################################
# CORE
# Do not modify this section

RUN apt-get update && apt-get install -y \
    pkg-config \
    cmake \
    openssl \
    wget \
    git \
    vim

RUN apt-get update && apt-get install -y \
    anacron \
    autoconf \
    automake \
    libarchive-dev \
    libtool \
    libopenblas-dev \
    libglib2.0-dev \
    gfortran \
    libxml2-dev \
    libxmlsec1-dev \
    libhdf5-dev \
    libgeos-dev \
    libsasl2-dev \
    libldap2-dev \
    squashfs-tools \
    build-essential

# Install Python requirements out of /tmp so not triggered if other contents of /code change
ADD requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt
RUN pip install django-rq

ADD . /code/

################################################################################
# PLUGINS
# You are free to uncomment the plugins that you want to use

# Install LDAP (uncomment if wanted)
# RUN pip install python3-ldap
# RUN pip install django-auth-ldap

# Install PAM Authentication (uncomment if wanted)
# RUN pip install django-pam

# Ensure Google Build Installed
# RUN pip install sregistry[google-build]

# Install Globus (uncomment if wanted)
# RUN /bin/bash /code/scripts/globus/globus-install.sh

# Install SAML (uncomment if wanted)
# RUN pip install python3-saml
# RUN pip install social-auth-core[saml]

################################################################################
# BASE

RUN mkdir -p /code && mkdir -p /code/images
RUN mkdir -p /var/www/images && chmod -R 0755 /code/images/

WORKDIR /code
RUN apt-get remove -y gfortran

RUN apt-get autoremove -y
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install crontab to setup job
RUN echo "0 0 * * * /usr/bin/python /code/manage.py generate_tree" >> /code/cronjob
RUN crontab /code/cronjob
RUN rm /code/cronjob

# Create hashed temporary upload locations
RUN mkdir -p /var/www/images/_upload/{0..9} && chmod 777 -R /var/www/images/_upload

CMD /code/run_uwsgi.sh

EXPOSE 3031
