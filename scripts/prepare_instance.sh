#!/bin/sh

# Change this to where you want to install. $HOME
# is probably a bad choice if it needs to be maintained
# by a group of people
INSTALL_ROOT=$HOME

# Prepare instance (or machine) with Docker, docker-compose, python

sudo apt-get update > /dev/null
sudo apt-get install -y git \
                        build-essential \
                        nginx \
                        python-dev

# Needed module for system python
wget https://bootstrap.pypa.io/get-pip.py
sudo /usr/bin/python get-pip.py
sudo pip install ipaddress
sudo pip install oauth2client


# Python 3
wget https://repo.continuum.io/archive/Anaconda3-4.2.0-Linux-x86_64.sh
bash Anaconda3-4.2.0-Linux-x86_64.sh -b

# You might already have anaconda installed somewhere
PATH=$HOME/anaconda3/bin:$PATH
rm Anaconda3-4.2.0-Linux-x86_64.sh 
export PATH

# Add docker key server
sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D

# Install Docker!
sudo apt-get update &&
sudo apt-get install apt-transport-https ca-certificates &&
sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
echo "deb https://apt.dockerproject.org/repo ubuntu-xenial main" | sudo tee --append /etc/apt/sources.list.d/docker.list
sudo apt-get update &&
apt-cache policy docker-engine
sudo apt-get update &&
sudo apt-get -y install linux-image-extra-$(uname -r) linux-image-extra-virtual &&
sudo apt-get -y install docker-engine &&
sudo service docker start

#sudo docker run hello-world
#make sure to add all users that will maintain / use the registry
sudo usermod -aG docker $USER

# Docker-compose
sudo apt -y install docker-compose

# Note that you will need to log in and out for changes to take effect

if [ ! -d $INSTALL_ROOT/singularity-registry ]
then
  cd $INSTALL_ROOT
  git clone https://www.github.com/singularityhub/sregistry.git
  cd sregistry
  docker build -t vanessa/sregistry .
  docker-compose up -d
fi
