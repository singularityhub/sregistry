---
layout: default
title: "Setup: Registration"
pdf: true
permalink: /setup-registration
toc: false
---

## Registration
We maintain a "registry of registries" ([https://singularityhub.github.io/containers](https://singularityhub.github.io/containers))(one registry to rule them all...) where you can easily have your registry's public images available for others to find. Adding your registry is easy - it comes down to automatically generating a file, adding it to the repo, and then doing a pull request (PR). Specifically:


### 1. Fork the repo
Fork the repo, and clone to your machine. That might look like this, given a username `vsoch`:

```
git clone https://www.github.com/vsoch/containers
cd containers
```

### 2. Generate your Metadata
Then use the manager to generate a markdown file for your registry. In this example, we have 
interactively shelled inside the `uwsgi` image for our sregistry like `docker run -it <container> bash` 
and are sitting in the `/code` folder.

```
# Inside the image
$ python manage.py register

Registry template written to taco-registry.md!

Your robot is at https://vsoch.github.io/robots/assets/img/robots/robot5413.png
1. Fork and clone https://www.github.com/singularityhub/containers
2. Add taco-registry.md to the registries folder
3. Download your robot (or add custom institution image) under assets/img/[custom/robots]
4. Submit a PR to validate your registry.
```

Specifically, this produces a markdown file in the present working directory (which is mapped to your host) that can be plopped into a folder. It is named based on your registry `uri`, and looks like this:

```
$ cat taco-registry.md 
---
layout: registry
title:  "Tacosaurus Computing Center"
base: http://127.0.0.1
date:   2017-08-30 17:45:44
author: vsochat
categories:
- registry
img: robots/robot5413.png
thumb: robots/robot5413.png # wget https://vsoch.github.io/robots/assets/img/robots/robot15570.png
tagged: taco
institution: Tacosaurus Computing Center
---

Tacosaurus Computing Center is a Singularity Registry to provide institution level Singularity containers.

```

At this point, you can send this file to `@vsoch` and she will be happy to add your 
registry to the... registry! If you want to customize your robot image, or submit
the file yourself via a pull request, continue reading!

### 3. Choose your image
For the image and thumbnail, we have a [database of robots](https://vsoch.github.io/robots) that we have randomly selected a robot for you. If you don't like your robot, feel free to browse and choose a different one. Importantly, you will need to add the robot to the github repo:

```
cd containers/assets/img/robots
wget https://vsoch.github.io/robots/assets/img/robots/robot15570.png
```

If you have some other custom image, add it to the "custom" folder. If it's not created yet, make it.

```
cd containers/assets/img
mkdir -p custom
cd custom
mv /path/to/institution/logo/taco-logo.png
```

Then for each of the `thumb` and `img` fields you would want to look like this:

```
img: custom/taco-logo.png
thumb: custom/taco-logo.png
```

### 4. Submit a PR
You can then add your files, and submit a PR to the main repo. We will have tests that ping your registry to ensure correct naming of files and registry address, along with a preview of the content that is added. If you want to prevew locally, you can run `jekyll serve`.


Great! Now that you have your accounts, you probably want to learn about how to build and push images! 
To push directly, you will first need to generate a [credential](/sregistry/credentials). If you 
have enabled the [Google Build+Github]({{ site.baseurl }}/plugin-google-build) plugin,
then you will be able to log in with GitHub, and connect GitHub repositories to build 
on commit. Either way, you should next read about the [client](/sregistry/client).

<div>
    <a href="/sregistry/setup-teams"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry/setup"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
