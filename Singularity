Bootstrap: docker
From: continuumio/miniconda3

%runscript

exec /opt/conda/bin/sregistry "$@"

%labels
maintainer vsochat@stanford.edu

%post
apt-get update && apt-get install -y git

# Dependncies
/opt/conda/bin/conda install -y numpy scikit-learn cython pandas

# Install Singularity Python
cd /opt
git clone -b development https://www.github.com/vsoch/singularity-python
cd singularity-python
/opt/conda/bin/pip install setuptools
/opt/conda/bin/pip install -r requirements.txt
/opt/conda/bin/pip install pyasn1==0.3.4
/opt/conda/bin/python setup.py sdist
/opt/conda/bin/python setup.py install
