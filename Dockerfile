FROM python:3.5.7
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive
ENV MESSAGELEVEL QUIET

ARG ENABLE_LDAP=false
ARG ENABLE_PAM=false
ARG ENABLE_PGP=false
ARG ENABLE_GOOGLEBUILD=false
ARG ENABLE_GLOBUS=false
ARG ENABLE_SAML=false

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

ADD . /code/

################################################################################
# PLUGINS
# You are free to uncomment the plugins that you want to use

# Install LDAP (uncomment if wanted)
RUN if $ENABLE_LDAP; then pip install python3-ldap ; fi;
RUN if $ENABLE_LDAP; then pip install django-auth-ldap ; fi;

# Install PAM Authentication (uncomment if wanted)
RUN if $ENABLE_PAM; then pip install django-pam ; fi;

# PGP keystore dependencies
RUN if $ENABLE_PGP; then pip install pgpdump>=1.4; fi;

# Ensure Google Build Installed
RUN if $ENABLE_GOOGLEBUILD; then pip install sregistry[google-build] ; fi;
ENV SREGISTRY_GOOGLE_STORAGE_PRIVATE=true

# Install Globus (uncomment if wanted)
RUN if $ENABLE_GLOBUS; then /bin/bash /code/scripts/globus/globus-install.sh ; fi;

# Install SAML (uncomment if wanted)
RUN if $ENABLE_SAML; then pip install python3-saml ; fi;
RUN if $ENABLE_SAML; then pip install social-auth-core[saml] ; fi;

################################################################################
# BASE

RUN mkdir -p /code && mkdir -p /code/images
RUN mkdir -p /var/www/images && chmod -R 0755 /code/images/

WORKDIR /code
RUN apt-get remove -y gfortran

RUN apt-get autoremove -y
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install crontab to setup jobs
RUN echo "0 0 * * * /usr/bin/python /code/manage.py generate_tree" >> /code/cronjob
RUN echo "0 * * * Mon /usr/bin/python /code/manage.py reset_container_limits" >> /code/cronjob
RUN echo "0 1 * * * /bin/bash /code/scripts/backup_db.sh" >> /code/cronjob
RUN echo "0 2 * * * /usr/bin/python /code/manage.py cleanup_dummy" >> /code/cronjob
RUN crontab /code/cronjob
RUN rm /code/cronjob

# Create hashed temporary upload locations
RUN mkdir -p /var/www/images/_upload/{0..9} && chmod 777 -R /var/www/images/_upload

CMD /code/run_uwsgi.sh

EXPOSE 3031
