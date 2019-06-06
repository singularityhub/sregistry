---
layout: default
title: "Installation: Web Server and Storage"
pdf: true
permalink: /install-server
toc: true
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
[vanessa/sregistry_nginx](https://hub.docker.com/r/vanessa/sregistry_nginx). If you want to build this image
on your own, you can change the section in the `docker-compose.yml` file to `build` instead of use an
`image`.  See [this issue](https://github.com/singularityhub/sregistry/issues/140) for the rationale for
having the pre-built image. To build, change this section:

```bash
nginx:
  restart: always
  image: vanessa/sregistry_nginx
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

If you don't care about user experience during updates and server downtime, you can just ignore this.

## Custom Domain

In the [config settings file](https://github.com/singularityhub/sregistry/blob/master/shub/settings/config.py#L30)
you'll find a section for domain names, and other metadata about your registry. You will need to update
this to be a custom hostname that you use, and custom names and unique resource identifiers for your
registry. For example, if you have a Google Domain and are using Google Cloud, you should be able to set it up using [Cloud DNS](https://console.cloud.google.com/net-services/dns/api/enable?nextPath=%2Fzones&project=singularity-static-registry&authuser=1). Usually this means
creating a zone for your instance, adding a Google Domain, and copying the DNS records for
the domain into Google Domains. Sometimes it can take a few days for changes to propogate.
We will discuss setting up https in a later section.

## Storage

By default, the containers that you upload to your registry will be stored "inside" the Docker container, specifically at the location `/var/www/images`. While it would not be reasonable to upload to Singularity Registry and then to a custom Storage, we have recently added
[custom builders]({{ site.url }}/install-builders) that can be used to push a recipe to Singularity Registry Server, and then trigger a cloud build that will be saved in some matching cloud storage.

If you choose the file system default storage, we map this location to the host in the base directory of `sregistry` in a folder called `images`. Equally, we map static web files to a folder named `static`. If you look in the [docker-compose.yml](https://github.com/singularityhub/sregistry/blob/master/docker-compose.yml) that looks something like this:


```yaml
    - ./static:/var/www/static
    - ./images:/var/www/images
```

The line reads specifically "map `./images` (the folder "images" in the base directory sregistry on the host) to (`:`) the folder `/var/www/images` (inside the container). This means a few important things:

 - if you container goes away and dies, your image files do not. If the folder wasn't mapped, this wouldn't be the case.
 - when the container is running, since Docker is run as sudo, you won't be able to interact with the files without sudo either.

Thus, you are free to test different configurations of mounting this folder. If you find a more reasonable default than is set, please [let us know!](https://www.github.com/singularityhub/sregistry/issues).


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

Once you have done this (and you are ready for https), you should use the `docker-compose.yml` and the `nginx.conf` provided in the folder [https](https). So do something like this:

```bash
mkdir http
mv nginx.conf http
mv docker-compose.yml http

cp https/docker-compose.yml .
cp https/nginx.conf.https nginx.conf
```

If you run into strange errors regarding any kind of authentication / server / nginx when you start the images, likely it has to do with not having moved these files, or a setting about https in the [settings](https://github.com/singularityhub/sregistry/tree/master/shub/settings). If you have trouble, please post an issue on the [issues board](https://www.github.com/singularityhub/sregistry/issues) and I'd be glad to help.


## Build the Image (Optional)
If you want to try it, you can build the image. Note that this step isn't necessary as the image is provided on [Docker Hub](https://hub.docker.com/r/vanessa/sregistry/). This step is optional. However, if you are developing you likely want to build the image locally. You can do:


```bash
cd sregistry
docker build -t vanessa/sregistry .
```

Next, why don't you [start Docker containers](/sregistry/install-containers) to get your own registry going.
