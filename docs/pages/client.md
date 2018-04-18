---
layout: default
title: sregistry client
pdf: true
permalink: /client
toc: false
---

<script src="assets/js/asciinema-player.js"></script>
<link rel="stylesheet" href="assets/css/asciinema-player.css"/>

The original Singularity Registry Client was provided by [Singularity Python](https://github.com/singularityware/singularity-python), however we have moved the client to have its own module under [sregistry-cli](https://github.com/singularityhub/sregistry-cli). We recommend that you use the latter, and ask for features or updates when necessary. For the new version, see the [getting started guide here](https://singularityhub.github.io/sregistry-cli/client-registry).

For the older version, you can use Singularity Python. A demo is provided below, along with the same documentation here [as a script](https://github.com/singularityware/singularity-python/blob/master/examples/registry/run_client.sh).

<asciinema-player src="assets/asciicast/registry.json" poster="data:text/plain,Intro to sregistry client" title="Introduction to the Singularity Registry client" author="vsochat@stanford.edu" cols="80" rows="40" speed="2.0" theme="asciinema"></asciinema-player>



## Install

### sregistry Installation
`sregistry` is the client for Singularity Registry server. To install, you can do the following:

```
git clone https://github.com/singularityware/sregistry-cli
cd sregistry-cli
python setup.py install
```

To check your install, run this command to make sure the `sregistry` client is found.

which sregistry


### Container Install
We have provided a Singularity build definition for you, for which you can use to build a container that serves as the sregistry client (and this will likely be provided on Singularity Hub so you don't even need to do that.) To build, do the following:

```
cd sregistry/

# Singularity 2.4 and up
sudo singularity build sregistry Singularity

# For Singularity earlier than 2.4 (deprecated)
singularity create --size 2000 sregistry
sudo singularity bootstrap sregistry Singularity
```

If you install via this option, you will want to make sure the container itself is somewhere on your path, with appropriate permissions for who you want to be able to use it.


## Commands
This brief tutorial assumes that you have [Singularity installed](https://singularityware.github.io/install-linux).

### Pull
Not shown in the demo above is the pull command, but it does the same thing as the singularity pull.

```
sregistry pull banana/pudding:milkshake
Progress |===================================| 100.0% 
Success! banana-pudding-milkshake.img
```

This is useful so that you can (locally from your registry) pull an image without needing to specify the registry url. It's also important because registry support will only be added to Singularity when the entire suite of compoenents are ready to go!


### Push

If you don't have an image handy, you can pull one from Singularity Hub:

```
singularity pull shub://vsoch/hello-world
```

And then a push to your registry looks like this:

```
sregistry push vsoch-hello-world-master.img --name dinosaur/avocado --tag delicious
sregistry push vsoch-hello-world-master.img --name meowmeow/avocado --tag nomnomnom
sregistry push vsoch-hello-world-master.img --name dinosaur/avocado --tag whatinthe
```

If you don't specify a tag, `latest` is used.

### List

List is a general command that will show a specific container, a specific collection, optionally with a tag. Examples are provided below:

```
# All collections
sregistry list

# A particular collection
sregistry list dinosaur

# A particular container name across collections
sregistry list /avocado

# A named container, no tag
sregistry list dinosaur/avocado

# A named container, with tag
sregistry list dinosaur/avocado:delicious
```

In addition to listing containers, `sregistry` can show you metadata! It does this by issuing an inspect command at upload time, so that no processing is needed on the server side. Singularity Registry is a Dockerized application, so it would require --privileged mode, which is a bad idea. Anyway, we can look at environment (`--env/-e`), runscript (`--runscript/-r`), tests (`--test/-t`), or `Singularity` definition recipe (`--deffile/-d`):

```
# Show me environment
sregistry list dinosaur/tacos:delicious --env

# Add runscript
sregistry list dinosaur/tacos:delicious --e --r

# Definition recipe (Singularity) and test
sregistry list dinosaur/tacos:delicious --d --t

# All of them
sregistry list dinosaur/tacos:delicious --e --r --d --t
```

### Delete
Delete requires the same authentication as push, and you will need to confirm with `yes/no`

```
sregistry delete dinosaur/tacos:delicious
sregistry list
```

if you want to force it, add `--force`

```
sregistry delete dinosaur/tacos:delicious --force
```

### Labels
Labels are important, and so they are represented as objects in the database for index, query, etc. Akin to containers, we can list and search:

```
# All labels
sregistry labels

# A specific key
sregistry labels --key maintainer

# A specific value
sregistry labels --value vanessasaur

# A specific key and value
sregistry labels --key maintainer --value vanessasaur
```

<div>
    <a href="/sregistry/interface"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry/client-singularity"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
