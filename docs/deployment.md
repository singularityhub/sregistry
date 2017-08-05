# Deployment
If starting from scratch, the [basic commands](../scripts/prepare_instance.sh) are provided that were used to set up an instance. This is just done once, and (in testing) was done on a fairly large fresh ubuntu:16.04 instance on Google Cloud. This setup is done only once, and requires logging in and out of the instance after installing Docker, but before bringing the instance up with `docker-compose`. A few important points:

- The `$INSTALL_BASE` is set by default to `/opt`. It is recommended to choose somewhere like `/opt` or `/share` that is accessible by all those who will maintain the installation. If you choose your home directory, you can expect that only you would see it.
- Anaconda3 is installed for python libraries needed for `docker-compose`. 
- Make sure to add all users to the docker group that need to maintain the application.

Updated docs on how to install Docker or docker-compose are provided for [installing Docker](http://54.71.194.30:4111/engine/installation) and [docker-compose](http://54.71.194.30:4111/compose/install/).

## Settings
See that folder called [settings](../shub/settings)? inside are a bunch of different starting settings for the application. We will change them in these files before we start the application. There are actually only two files you need to poke into, generating a [settings/secrets.py](../shub/settings/secrets.py) for application secrets, and [settings/config.py](../shub/settings/config.py) to configure your database and registry information.

### Secrets
There should be a file called `secrets.py` in the shub settings folder (it won't exist in the repo, you have to make it), in which you will store the application secret and other social login credentials. First, create this file

```bash
touch shub/settings/secrets.py
```

and inside you want to add a `SECRET_KEY`. You can use the [secret key generator](http://www.miniwebtool.com/django-secret-key-generator/) to make a new secret key, and call it `SECRET_KEY` in your `secrets.py` file, like this:

```      
SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```

### Config
In the [config.py](../shub/settings/config.py) you need to define the following:


#### Domain Name
Singularity Registry should have a domain. It's not required, but it makes it much easier for yourself and users to remember the address. The first thing you should do is change the `DOMAIN_NAME_*` variables in your settings [settings/main.py](../shub/settings/main.py).

For local testing, you will want to change `DOMAIN_NAME` and `DOMAIN_NAME_HTTP` to be localhost. Also note that I've set the regular domain name (which should be https) to just http because I don't have https locally:

```
DOMAIN_NAME = "http://127.0.0.1"
DOMAIN_NAME_HTTP = "http://127.0.0.1"
#DOMAIN_NAME = "https://singularity-hub.org"
#DOMAIN_NAME_HTTP = "http://singularity-hub.org"
```

It's up to the deployer to set one up a domain or subdomain for the server. Typically this means going into the hosting account to add the A and CNAME records, and then update the DNS servers. Since every host is a little different, I'll leave this up to you, but [here is how I did it on Google Cloud](https://cloud.google.com/dns/quickstart).


#### Registry Contact
You need to define a registry uri, and different contact information:

```
HELP_CONTACT_EMAIL = 'vsochat@stanford.edu'
HELP_INSTITUTION_SITE = 'srcc.stanford.edu'
REGISTRY_NAME = "Tacosaurus Computing Center"
REGISTRY_URI = "taco"
```

The `HELP_CONTACT_EMAIL` should be an email address that you want your users (and/or visitors to your registry site, if public) to find if they need help. The `HELP_INSTITUTION_SITE` is any online documentation that you want to be found in that same spot. Finally, `REGISTRY_NAME` is the long (human readable with spaces) name for your registry, and `REGISTRY_URI` is a string, all lowercase, 12 or fewer characters to describe your registry.


#### Database
By default, the database itself will be deployed as a postgres image called `db`. You probably don't want this for production (for example, I use a second instance with postgres and a third with a hot backup, but it's an ok solution for a small cluster or single user. Either way, we recommend backing it up every so often.

When your database is set up, you can define it in your secrets.py and it will override the Docker image one in the settings/main.py file. It should look something like this

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dbname',
        'USER': 'dbusername',
        'PASSWORD':'dbpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```





## Setup
Before doing `docker-compose up -d` to start the containers, there are some specific things that need to be set up.

### Under Maintenance Page
If it's ever the case that the Docker images need to be brought down for maintenance, a static fallback page should be available to notify the user. If you noticed in the [prepare_instance.sh](../scripts/prepare_instance.sh) script, one of the things we installed is nginx (on the instance). This is because we need to use it to get proper certificates for our domain (for https). Before you do this, you might want to copy the index that we've provided to replace the default (some lame page that says welcome to Nginx!) to one that you can show when the server is undergoing maintainance.

```bash
cp $INSTALL_ROOT/sregistry/scripts/nginx-index.html /var/www/html/index.html
rm /var/www/html/index.nginx-debian.html
```

### SSL
Getting https certificates is really annoying, and getting `dhparams.pem` takes forever. But after the domain is obtained, it's important to do. Again, remember that we are working on the host, and we have an nginx server running. You should follow the instructions (and I do this manually) in [generate_cert.sh](../scripts/generate_cert.sh). It basically comes down to:

 - starting nginx
 - installing tiny acme
 - generating certificates
 - using tinyacme to get them certified
 - moving them to where they need to be.
 - add a reminder or some other method to renew within 89 days

Once you have done this, you should use the `docker-compose.yml` and the `nginx.conf` provided in the folder [https](https). So do something like this:

```bash
mkdir http
mv nginx.conf http
mv docker-compose.yml http

mv https/docker-compose.yml $PWD
mv https/nginx.conf $PWD
```

Most importantly, we use a text file to make sure that we generate a single certificate that covers both www* and without. This part of the [generate_cert.sh](../scripts/generate_cert.sh) you will need to update the location (town, city, etc) along with your email and the domain you are using:

```bash
cat > csr_details.txt <<-EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
req_extensions = req_ext
distinguished_name = dn
 
[ dn ]
C=US
ST=California
L=San Mateo County
O=End Point
OU=SingularityRegistry
emailAddress=youremail@university.edu
CN = www.domain.edu
 
[ req_ext ]
subjectAltName = @alt_names
 
[ alt_names ]
DNS.1 = domain.edu
DNS.2 = www.domain.edu
EOF
```

Specifically, pay close attention to the fields in the last two sections that need to be customized for the domain and region.

If you run into strange errors regarding any kind of authentication / server / nginx when you start the images, likely it has to do with not having moved these files, or a setting about https in the [settings](../shub/settings). If you have trouble, please post an issue on the [issues board](https://www.github.com/singularityhub/sregistry/issues) and I'd be glad to help.


## Build the Image
Next, you should build your image, and run the application with `docker-compose`. By the time this code is public we should also be providing the image on Docker Hub, so likely you can skip the build:

```bash
cd sregistry
docker build -t vanessa/sregistry .
docker-compose up -d
```

The `-d` means detached, and that you won't see any output (or errors) to the console. You can easily restart and stop containers, either specifying the container name(s) or leaving blank to apply to all containers. Note that these commands must be run in the folder with the `docker-compose.yml`:

```
docker-compose restart uwsgi worker nginx
docker-compose stop
```

When you do `docker-compose up -d` the application should be available at `http://127.0.0.1/`, and if you've configured https, `https://127.0.0.1/`. If you need to shell into the application, for example to debug with `python manage.py shell` you can get the container id with `docker ps` and then do:

```
NAME=$(docker ps -aqf "name=singularityregistry_uwsgi_1")
docker exec -it ${NAME} bash
```

Good job! Now it's time to read the [configuration](config.md) guide to better understand how to configure and interact with your Singularity Registry.
