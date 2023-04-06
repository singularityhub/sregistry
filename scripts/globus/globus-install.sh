#!/bin/bash

# Install python packages

pip install pip --upgrade
pip install globus-cli globus-sdk[jwt]

# Install globusconnectpersonal

cd /opt
wget https://s3.amazonaws.com/connect.globusonline.org/linux/stable/globusconnectpersonal-2.3.4.tgz && \
     tar xzf globusconnectpersonal-2.3.4.tgz && \
     mv globusconnectpersonal-2.3.4 globus && \
    sed -i -e 's/-eq 0/-eq 999/g' /opt/globus/globusconnectpersonal

git clone https://github.com/sirosen/globusconnectpersonal-py3-patched && \
    cp globusconnectpersonal-py3-patched/gc*.py /opt/globus


# Create globus user
useradd -ms /bin/bash tunel-user
echo "tunel-user ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
