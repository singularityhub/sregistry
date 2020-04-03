---
title: "Installation: Web Server and Storage"
pdf: true
---

# Installation: Web Server and Storage

Before doing `docker-compose up -d` to start the containers, there are some specific things that need to be set up.

## Nginx

This section is mostly for your FYI. The nginx container that we use is a custom compiled
nginx that includes the [nginx uploads module](https://www.nginx.com/resources/wiki/modules/upload/).
This allows us to define a server block that will accept multipart form data directly, and 
allow uploads directly to the server without needing to stress the uwsgi application. The uploads
are a ton faster! You shouldn't need to do anything special when you bring up the container, but
keep in mind that if you are deploying this without docker containers (e.g., using your own
web server) you will need to equivalently compile nginx with the module enabled. A standard
server without this module will no longer work. Currently, we use an image provided on Docker Hub,
[quay.io/vanessa/sregistry_nginx](https://hub.docker.com/r/quay.io/vanessa/sregistry_nginx). If you want to build this image
on your own, you can change the section in the `docker-compose.yml` file to `build` instead of use an
`image`.  See [this issue](https://github.com/singularityhub/sregistry/issues/140) for the rationale for
having the pre-built image. To build, change this section:

```bash
nginx:
  restart: always
  image: quay.io/vanessa/sregistry_nginx
  ports:
    - "80:80"
  volumes:
    - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    - ./uwsgi_params.par:/etc/nginx/uwsgi_params.par:ro
  volumes_from:
    - uwsgi
  links:
    - uwsgi
    - db
``` 

to this

```bash
nginx:
  restart: always
  build: nginx
  ports:
    - "80:80"
  volumes:
    - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    - ./uwsgi_params.par:/etc/nginx/uwsgi_params.par:ro
  volumes_from:
    - uwsgi
  links:
    - uwsgi
    - db
```

the image will be built from the `nginx` folder provided in the repository.

## Under Maintenance Page

If it's ever the case that the Docker images need to be brought down for maintenance, a static fallback page should be available to notify the user. If you noticed in the [prepare_instance.sh](https://github.com/singularityhub/sregistry/blob/master/scripts/prepare_instance.sh) script, one of the things we installed is nginx (on the instance). This is because we need to use it to get proper certificates for our domain (for https). Before you do this, you might want to copy the index that we've provided to replace the default (some lame page that says welcome to Nginx!) to one that you can show when the server is undergoing maintainance.

```bash
cp $INSTALL_ROOT/sregistry/scripts/nginx-index.html /var/www/html/index.html
rm /var/www/html/index.nginx-debian.html
```

If you want your page to use the same SSL certificates, a nginx-default.conf is also
provided that will point to the same certificates on the server (generation discussed later).
Please execute this command only after the certificates have been generated, or you won't be able to generate them:

```bash
cp $INSTALL_ROOT/sregistry/scripts/nginx-default.conf /etc/nginx/conf.d/default.conf
```

If you don't care about user experience during updates and server downtime, you can just ignore this.

## Custom Domain

In the [config settings file](https://github.com/singularityhub/sregistry/blob/master/shub/settings/config.py#L30)
you'll find a section for domain names, and other metadata about your registry. You will need to update
this to be a custom hostname that you use, and custom names and unique resource identifiers for your
registry. For example, if you have a Google Domain and are using Google Cloud, you should be able to set it up using [Cloud DNS](https://console.cloud.google.com/net-services/dns/api/enable?nextPath=%2Fzones&project=singularity-static-registry&authuser=1). Usually this means
creating a zone for your instance, adding a Google Domain, and copying the DNS records for
the domain into Google Domains. Sometimes it can take a few days for changes to propogate.
You are strongly encouraged to register both `your.domain.com`, as well as `www.your.domain.com` and have them point to the same IP address.
We will discuss setting up https in a later section.

## Storage

For Singularity versions prior to 1.1.24, containers that were uploaded to your registry
were stored on the filesystem, specifically at `/var/www/images` that was bound to the host
at `images`. We did this by way of using a custom nginx image with the nginx upload module
enabled (see [this post](https://vsoch.github.io/2018/django-nginx-upload/) for an example).

There is also the other option to use [custom builders]({{ site.url }}/install-builders) 
that can be used to push a recipe to Singularity Registry Server, and then trigger a 
cloud build that will be saved in some matching cloud storage.

### Default

However for versions 1.1.24 and later, to better handle the Singularity `library://`
client that uses Amazon S3, we added a [Minio Storage](https://docs.min.io/docs/python-client-api-reference.html#presigned_get_object) 
backend, or another container (minio) that is deployed alongside Singularity Registry server.
If you look in the [docker-compose.yml](https://github.com/singularityhub/sregistry/blob/master/docker-compose.yml) that looks something like this:

```
minio:
  image: minio/minio
  volumes:
    - ./minio-images:/images
  env_file:
   - ./.minio-env
  ports:
   - "9000:9000"  
  command: ["server", "images"]
```


At the time of develpoment we are using this version of minio:

```
/ # minio --version
minio version RELEASE.2020-04-02T21-34-49Z
```

which you can set in the docker-compose.yml file to pin it. Notice that we bind the
folder "minio-images" in the present working directory to /images in the container,
which is where we are telling minio to write images to the filesystem. This means
that if your container goes away, the image files will still be present on the host.
For example, after pushing two images, I can see them organized by bucket, collection,
then container name with hash.

```
$ tree minio-images/
minio-images/
└── sregistry
    └── test
        ├── big:sha256.92278b7c046c0acf0952b3e1663b8abb819c260e8a96705bad90833d87ca0874
        └── container:sha256.c8dea5eb23dec3c53130fabea451703609478d7d75a8aec0fec238770fd5be6e
```

### Configuration
For secrets (the access and secret key that are used to create the container) 
we are reading in environment variables for the server in `.minio-env`
that looks like this:

```bash
MINIO_ACCESS_KEY=minio
MINIO_SECRET_KEY=minio123
```

**You should obviously change the access key and secret in the minio-env file!**
This is also bound to the uwsgi container, so that the generation of the minio
storage can be authenticated by the uwsgi container, which is the interface between
the Singularity client and minio. For variables that aren't secrets, you can look
in `shub/settings/config.py` and look for the "Storage" section with various
minio variables:

```python
MINIO_SERVER = "minio:9000"  # Internal to sregistry
MINIO_EXTERNAL_SERVER = (
    "127.0.0.1:9000"  # minio server for Singularity to interact with
)
MINIO_BUCKET = "sregistry"
MINIO_SSL = False  # use SSL for minio
MINIO_SIGNED_URL_EXPIRE_MINUTES = 5
MINIO_REGION = "us-east-1"
```

Since the container networking space is different from what the external
Singularity client interacts with, we define them both here. If you deploy
a minio server external to the docker-compose.yml, you can update both of
these URLs to be the url to access it. The number of minutes for the signed
url to expire applies to both PUT (upload) and GET (download) requests.
Note that SSL instructions are not written yet for minio.

## SSL

Getting https certificates is really annoying, and getting `dhparams.pem` takes forever. But after the domain is obtained, it's important to do. Again, remember that we are working on the host, and we have an nginx server running. You should follow the instructions (and I do this manually) in [generate_cert.sh](https://github.com/singularityhub/sregistry/blob/master/scripts/generate_cert.sh). 

 - starting nginx
 - installing certbot
 - generating certificates
 - linking them to where the docker-compose expects them
 - add a reminder or some other method to renew within 89 days

With certbot, you should be able to run `certbot renew` when the time to renew comes up. There is also an [older
version](https://github.com/singularityhub/sregistry/blob/master/scripts/generate_cert_tiny-acme.sh) that uses tiny-acme instead of certbot. For this second option, it basically comes down to:

 - starting nginx
 - installing tiny acme
 - generating certificates
 - using tinyacme to get them certified
 - moving them to where they need to be.
 - add a reminder or some other method to renew within 89 days

Once you have done this (and you are ready for https), you should use the `docker-compose.yml` and the `nginx.conf` provided in the folder [https](https://github.com/singularityhub/sregistry/blob/master/https/). So do something like this:

```bash
mkdir http
mv nginx.conf http
mv docker-compose.yml http

cp https/docker-compose.yml .
cp https/nginx.conf.https nginx.conf
```

If you run into strange errors regarding any kind of authentication / server / nginx when you start the images, likely it has to do with not having moved these files, or a setting about https in the [settings](https://github.com/singularityhub/sregistry/tree/master/shub/settings). If you have trouble, please post an issue on the [issues board](https://www.github.com/singularityhub/sregistry/issues) and I'd be glad to help.


## Build the Image (Optional)
If you want to try it, you can build the image. Note that this step isn't necessary as the image is provided on [Quay.io]({{ site.registry }}). This step is optional. However, if you are developing you likely want to build the image locally. You can do:


```bash
cd sregistry
docker build -t quay.io/vanessa/sregistry .
```

Next, why don't you [start Docker containers](containers) to get your own registry going.
