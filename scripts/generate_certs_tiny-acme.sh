#! /bin/bash
#
# nginx should be installed on the host machine
#
#

INSTALL_ROOT=${1}
EMAIL=${2}
DOMAIN=${2}
STATE=${3:-California}
COUNTY=${4:-San Mateo County}

sudo mkdir /opt/acme_tiny
cd /tmp && git clone https://github.com/diafygi/acme-tiny
sudo mv acme-tiny /opt/acme-tiny/
sudo chown "$USER" -R /opt/acme-tiny

# Create a directory for the keys and cert
cd "$INSTALL_ROOT"/sregistry

# If you started the images, stop nginx
docker-compose stop nginx
sudo service nginx start

# backup old key and cert
if [ -f "/etc/ssl/private/domain.key" ]
   then
   sudo cp /etc/ssl/private/domain.key{,.bak."$(date +%s)"}
fi

if [ -f "/etc/ssl/certs/chained.pem" ]
   then
   sudo cp /etc/ssl/certs/chained.pem{,.bak."$(date +%s)"}
fi

if [ -f "/etc/ssl/certs/domain.csr" ]
   then
   sudo cp /etc/ssl/certs/domain.csr{,.bak."$(date +%s)"}
fi

# Generate a private account key, if doesn't exist
if [ ! -f "/etc/ssl/certs/account.key" ]
   then
   openssl genrsa 4096 > account.key && sudo mv account.key /etc/ssl/certs
fi

# Add extra security
if [ ! -f "/etc/ssl/certs/dhparam.pem" ]
   then
   openssl dhparam -out dhparam.pem 4096 && sudo mv dhparam.pem /etc/ssl/certs
fi

if [ ! -f "csr_details.txt" ]
then

cat > csr_details.txt <<-EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
req_extensions = req_ext
distinguished_name = dn
 
[ dn ]
C=US
ST=$STATE
L=$COUNTY
O=End Point
OU=$DOMAIN
emailAddress=$EMAIL
CN = www.$DOMAIN
 
[ req_ext ]
subjectAltName = @alt_names
 
[ alt_names ]
DNS.1 = $DOMAIN
DNS.2 = www.$DOMAIN
EOF

fi
 
# Call openssl
openssl req -new -sha256 -nodes -out domain.csr -newkey rsa:2048 -keyout domain.key -config <( cat csr_details.txt )

# Create a CSR for $DOMAIN
#sudo openssl req -new -sha256 -key /etc/ssl/private/domain.key -subj "/CN=$DOMAIN" > domain.csr
sudo mv domain.csr /etc/ssl/certs/domain.csr
sudo mv domain.key /etc/ssl/private/domain.key

# Create the challenge folder in the webroot
sudo mkdir -p /var/www/html/.well-known/acme-challenge/
sudo chown "$USER" -R /var/www/html/

# Get a signed certificate with acme-tiny
#docker-compose stop nginx
python /opt/acme-tiny/acme_tiny.py --account-key /etc/ssl/certs/account.key --csr /etc/ssl/certs/domain.csr --acme-dir /var/www/html/.well-known/acme-challenge/ > ./signed.crt

wget -O - https://letsencrypt.org/certs/lets-encrypt-x3-cross-signed.pem > intermediate.pem
cat signed.crt intermediate.pem > chained.pem
sudo mv chained.pem /etc/ssl/certs/
rm signed.crt intermediate.pem

# Stop nginx
sudo service nginx stop

cd "$INSTALL_ROOT"/sregistry
docker-compose up -d
