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

Encapsulation of scientific workflows is essential for reproducibility of science. Container and virtualization technologies such as Docker and virtual machines have helped with the sharing of scientific workflows, but it wasn't until the introduction of the Singularity software [@Kurtzer2017-x] that these workflows could be securely deployed on local cluster resources. With Singularity came a free cloud service, Singularity Hub [@SingularityHub], developed by Stanford University Research Computing that offered to build research containers from build recipes in Github repositories. While this tool was useful to many individual users, unfortunately the setup did not scale to meet the needs of larger institutions that wanted to integrate and scale custom build environments.
 
Singularity Registry (sregistry) [@SingularityRegistryGithub] was developed to meet the need for an institution or individual to build and share Singularity images. The Dockerized web application empowers the Singularity community to build images on their cluster or local resource, and push them securely to the application. Public images are available for programmatic usage for anyone, and private images to authenticated users with the Singularity command line software. Sregistry allows for numerous authentication backends, tracks downloads and starring of images, tagging and versioning, search, and provides an interactive treemap visualization to assess size of image collections relative to one another. 

![Singularity Collection Sizes](sizes.png)

Importantly, behind sregistry is a growing and thriving community of scientists, high performance computing (HPC) admins, and research software engineers that are incentivized to generate and share reproducible containers. Complete documentation including setup, deployment, and usage, is available [@SRegistry], and the developers welcome contribution and feedback in any form.

# References
