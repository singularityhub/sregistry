FROM python:3.5.1
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y \
    anacron \
    libopenblas-dev \
    libglib2.0-dev \
    gfortran \
    pkg-config \
    libxml2-dev \
    libxmlsec1-dev \
    libhdf5-dev \
    libgeos-dev \
    build-essential \
    openssl \
    wget \
    vim

# Install Singularity
RUN git clone https://www.github.com/singularityware/singularity.git
WORKDIR singularity
RUN ./autogen.sh && ./configure --prefix=/usr/local && make && make install

# Install Python requirements out of /tmp so not triggered if other contents of /code change
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

RUN mkdir /code
RUN mkdir -p /var/www/images

WORKDIR /code
RUN apt-get remove -y gfortran

RUN apt-get autoremove -y
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ADD . /code/

# Install crontab to setup job
RUN echo "0 0 * * * /usr/bin/python /code/manage.py generate_tree" >> /code/cronjob
RUN crontab /code/cronjob
RUN rm /code/cronjob

CMD /code/run_uwsgi.sh

EXPOSE 3031
