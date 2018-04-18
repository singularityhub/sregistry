---
layout: default
title: Singularity Client
pdf: true
permalink: /client-singularity
toc: false
---

# Singularity Pull

Support for Singularity Registry Server pull via the Singularity software was added to the development branch in a [recent pull request](https://github.com/singularityware/singularity/pull/889), and will be in the release of Singularity 2.4 [demo](https://asciinema.org/a/134694?speed=3).

## Install

### Local Installation
You will want to install Singularity first:

```
git clone https://github.com/singularityware/singularity
cd singularity
./autogen.sh
./configure --prefix=/usr/local
make
sudo make install
```

## Pull

and then, given an image called "tacos" in collection "dinosaur" with tag "latest" (`shub://127.0.0.1/dinosaur/tacos:latest`) and a registry serving on your localhost (`127.0.0.1`) you would pull the image using Singularity as follows:

```
singularity pull shub://127.0.0.1/dinosaur/tacos:latest
```

### How is it different? 

This is different than the traditional shub pull command (which uses Github as a namespace) because of the inclusion of the registry uri. On Github, if you imagine that there was a repo named "tacos" owned by user "dinosaur" that pull would look different (and still work):

```
singularity pull shub://dinosaur/tacos:latest
```

<div>
    <a href="/sregistry/client"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry/plugins"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
