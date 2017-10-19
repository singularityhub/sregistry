---
title: 'Singularity Registry: Open Source Registry for Singularity Images'
tags:
  - containers
  - singularity
  - linux
  - registry
authors:
 - name: Vanessa Sochat
   orcid: 0000-0002-4387-3819
   affiliation: 1
affiliations:
 - name: Stanford University Research Computing
   index: 1
date: 26 September 2017
bibliography: paper.bib
---

# Summary

Singularity Registry is a non-centralized free and Open Source infrastructure to facilitate management and sharing of institutional or personal containers.

A container is the encapsulation of an entire computational environment that can be run consistently if the platform supports it. It is an aid in reproducibility [@Moreews2015-dy, @Belmann2015-eb, @Boettiger2014-cz, @Santana-Perez2015-wo, @Wandell2015-yt] because different researchers can run the exact same software stack on different underlying (Linux Intel) systems. Docker [@Merkel2014-da] has become popular as a general container system because it allows software to be bundled with administrator privileges, however,  it poses great security risks if installed on a multi-user, shared computational resource, and thus Docker has not had admission to these high performance computing (HPC) environments. Singularity [@Kurtzer2017-xj] offers similar features to Docker for software deployment but does not not allow the user to escalate to root, and so it has been easy to accept in HPC environments. Since its introduction, Singularity has been deployed in over 50 HPC resources across the globe.

## Sharing of Containers for Reproducible Science
Essential to the success of Singularity is not just creation of images, but sharing of them. To address this need, a free cloud service, Singularity Hub [@SingularityHub], was developed to build and share containers for scientists simply by way of building containers from a specification file in a version controlled Github repository. This setup is ideal given a small number of containers, each belonging in one Github repository, but is not optimal for institutions that wanted to build at scale using custom strategies.

Singularity Registry (sregistry) [@SingularityRegistryGithub] was developed to empower an institution or individual to build at scale, and push images that can be private or public to their own hosted registry.  It is the first user and institution installable, non-centralized Open Source infrastructure to faciliate the sharing of containers. While Singularity Hub works with cloud builders and object storage,  Singularity Registry is optimized for storage on a local filesystem and any choice of builder (e.g., continuous integration ([Travis](https://www.travis-ci.org), [Circle](https://circleci.com/)), cluster or private node, or separate server). A Registry is also customized with a center's name, and links to appropriate help contacts.

![Singularity Registry Home](registry-home.png)

The Registry, along with native integration into the Singularity software, includes several tools for organization, analysis, and logging of image metrics and usage. Administrators can control the ability for users or the larger community to create accounts, and give finely tuned access (e.g., an expiring token) to share containers. An application programming interface (API) exposes metadata such as container sizes, versioning, and build times. Every time a container is used, or starred by a user, the Registry keeps a record. This kind of metadata not only about containers but about their usage is highly useful to get feedback about highly used containers and general container use.

Public images are available for programmatic usage for anyone, and private images to authenticated users with the Singularity command line software. Sregistry allows for numerous authentication backends, tracks downloads and starring of images, tagging and versioning, search, and provides an interactive treemap visualization to assess size of image collections relative to one another.

![Singularity Collection Sizes](sizes.png)

Importantly, behind sregistry is a growing and thriving community of scientists, high performance computing (HPC) admins, and research software engineers that are incentivized to generate and share reproducible containers. Complete documentation including setup, deployment, and usage, is available [@SRegistry], and the developers welcome contribution and feedback in any form. Singularity Registry empowers the larger scientific community to build reproducible containers on their cluster or local resource, push them securely to the application, and share them toward transparency and reproducibility for discovery in science.


# References
