#! /bin/bash
#
# nginx should be installed on the host machine
#
#

EMAIL=${1}
DOMAIN=${2}
INSTALL_ROOT=$HOME

# Install certbot (if not already done)
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install python-certbot-nginx

# Get certificates (might need sudo)
certbot certonly --nginx -d "${DOMAIN}" -d "www.${DOMAIN}" --email "${EMAIL}" --agree-tos --redirect

# The prompt is interactive, and will show the locations of certificates

# Obtaining a new certificate
# Performing the following challenges:
# http-01 challenge for containers.page
# http-01 challenge for www.containers.page
# Waiting for verification...
# Cleaning up challenges

# IMPORTANT NOTES:
# - Congratulations! Your certificate and chain have been saved at:
#   /etc/letsencrypt/live/containers.page/fullchain.pem
#   Your key file has been saved at:
#   /etc/letsencrypt/live/containers.page/privkey.pem
#   Your cert will expire on 2019-09-04. To obtain a new or tweaked
#   version of this certificate in the future, simply run certbot
#   again. To non-interactively renew *all* of your certificates, run
#   "certbot renew"
# - Your account credentials have been saved in your Certbot
#   configuration directory at /etc/letsencrypt. You should make a
#   secure backup of this folder now. This configuration directory will
#   also contain certificates and private keys obtained by Certbot so
#   making regular backups of this folder is ideal.
# - If you like Certbot, please consider supporting our work by:

#   Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
#   Donating to EFF:                    https://eff.org/donate-le

# Since the containers expect these files to be in /etc/ssl, copy there
# This CANNOT be a link.
sudo cp /etc/letsencrypt/live/containers.page/fullchain.pem /etc/ssl/certs/chained.pem
sudo cp /etc/letsencrypt/live/containers.page/privkey.pem /etc/ssl/private/domain.key

# Create recursive backup
backup=$(echo /etc/letsencrypt{,.bak.$(date +%s)} | cut -d ' ' -f 2)
sudo cp -R /etc/letsencrypt $backup

# Add extra security
if [ ! -f "/etc/ssl/certs/dhparam.pem" ]
   then
   openssl dhparam -out dhparam.pem 4096 && sudo mv dhparam.pem /etc/ssl/certs
fi

# Stop nginx
sudo service nginx stop

cd $INSTALL_ROOT/sregistry
docker-compose up -d
