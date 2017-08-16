FROM python:3.5.1
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y \
    libopenblas-dev \
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


RUN pip install cython
RUN pip install numpy
RUN pip install scikit-learn pandas h5py matplotlib
RUN pip install uwsgi
RUN pip install Django==1.11.2
RUN pip install social-auth-app-django
RUN pip install social-auth-core[saml]
RUN pip install python-social-auth
RUN pip install djangorestframework
RUN pip install markdown
RUN pip install django-filter
RUN pip install django-extensions
RUN pip install django-taggit
RUN pip install django-form-utils
RUN pip install django-crispy-forms
RUN pip install django-taggit-templatetags
RUN pip install django-dirtyfields
RUN pip install psycopg2
RUN pip install numexpr
RUN pip install shapely
RUN pip install Pillow
RUN pip install requests
RUN pip install requests-oauthlib
RUN pip install python-openid
RUN pip install django-sendfile
RUN pip install django-polymorphic
RUN pip install networkx
RUN pip install celery[redis]
RUN pip install django-celery
RUN pip install scikit-learn
RUN pip install django-cleanup
RUN pip install django-chosen
RUN pip install opbeat
RUN pip install 'django-hstore==1.3.5'
RUN pip install django-datatables-view
RUN pip install simplejson
RUN pip install singularity
RUN pip install django-gravatar2
RUN pip install pygments
RUN pip install google-api-python-client
RUN pip install google
RUN pip install oauth2client==3.0
RUN pip install retrying
RUN pip install django-rest-swagger
RUN pip install django-user-agents
RUN pip install django-guardian
RUN pip install pytz
RUN pip install python3-saml

# Install Singularity
RUN git clone https://www.github.com/singularityware/singularity.git
WORKDIR singularity
RUN ./autogen.sh && ./configure --prefix=/usr/local && make && make install

RUN mkdir /code
RUN mkir -p /var/www/images

WORKDIR /code
RUN /usr/bin/yes | pip uninstall cython
RUN apt-get remove -y gfortran

RUN apt-get autoremove -y
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


ADD . /code/

# Install crontab to setup job
RUN apt-get update && apt-get install -y gnome-schedule
RUN echo "0 0 * * * /usr/bin/python /code/manage.py generate_tree" >> /code/cronjob
RUN crontab /code/cronjob
RUN rm /code/cronjob

CMD /code/run_uwsgi.sh

EXPOSE 3031
