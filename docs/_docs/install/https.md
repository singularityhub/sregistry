---
title: Configure https for your server
pdf: true
toc: true
---

# Configure HTTPs

## Get a hostname
Recall that the first step to get https is to have a hostname. You can use Google
Domains, or you can also create an account on [https://www.dynu.com](https://www.dynu.com) (It’s free).
Log into your account and under the Control Panel go to DDNS Services. On the next page, click the **+ Add** button, and fill out the Host and Top Level fields under Option 1 using whatever you like. 
This will be how users access your server (e.g., `sregistry.dynu.net)`. Click + Add.

 - On the next page, change the IPv4 Address to the IP address for your droplet. Change the TTL to 60. Click Save.
 - With a few minutes, you should be able to access your server using that hostname.


## Test Nginx

In the install script, we installed nginx. Now, you merely need to start it (it might
already be started).

```bash
$ sudo service nginx start
```

For this next step, we are still working on the host where you will run your container. What we first need to do is generate certificates, start a local web server, and ping "Let's Encrypt" to verify that we own the server, and then sign the certificates.

### SSL Certificates
We'll use "certbot" to install and renew certificates.

#### Step 1. Set some variables

First we'll set some variables that are used in later steps.

```bash
EMAIL="youremail@yourdomain.com"
DOMAIN="containers.page"
```

The email you set here will be used to send you renewal reminders at 20 days, 10 days, and 1 day before expiry (super helpful!)

#### Step 2. Install certbot

Certbot automates certificate generation and renewal. In other words, it makes it really easy to setup SSL.

```bash
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install python-certbot-nginx
```

#### Step 3. Get certificates with certbot

Now obtain a certificate by running this command.  Note that if you aren't using a container, or you aren't the root user, you might need to add `sudo`.

```bash
certbot certonly --nginx -d "${DOMAIN}" -d "www.${DOMAIN}" --email "${EMAIL}" --agree-tos --redirect
```

Equivalently, if your domain doesn't have `www.` you can remove the second `-d` argument.

#### Step 4. Stop nginx

Now we need to stop nginx because we have what we need from it!

```bash
sudo service nginx stop
```

#### Step 5. Copy certs to a new location

Now we'll move the certs to where they're expected later.

```bash
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /etc/ssl/certs/chained.pem
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /etc/ssl/private/domain.key
sudo cp /etc/letsencrypt/ssl-dhparams.pem /etc/ssl/certs/dhparam.pem
```

#### Step 6. Renewal (and remembering to renew!)

Certificates expire after 90 days. You'll get reminders at 20 days, 10 days, and 1 day before expiry to the email you set before. Before the cert expires, you can run this command to renew:

```bash
sudo certbot renew
```

{% include alert.html title="Important!" content="Before renewing you need to stop the docker container running expfactory and start nginx outside of docker." %}

The commands to stop the nginx container and
renew the certificates might look like this (this is for typical Ubuntu or similar).

```bash
docker-compose stop nginx
sudo service nginx start
sudo certbot renew
sudo service nginx stop
docker-compose start nginx
```

And then issue the command to start your container.

Importantly, when you start the container (that will be generated in the next steps)
you will need to bind to these files on the host, and
expose ports 80 and 443 too.
