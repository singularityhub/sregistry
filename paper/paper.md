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

## A Need for Reproducible Science
Using computational methods to answer scientific questions of interest is an important task to increase our knowledge about the world. Along with careful assembly of protocol and relevant datasets, the scientist that faces this challenging task must also write software to perform the analysis. Running the software in combination with the dataset is a typical recipe for scientific discovery. When such a result comes to fruition, the scientist writes it up for publication in a scientific journal. 

The ability to replicate a result, then, can be thought of as increasing our confidence in the finding. The extent to which a published finding affords a second scientist to repeat the steps to achieve the result is called reproducibility. Reproducibility, in that it allows for repeated testing of an interesting question to validate knowledge about the world, is a foundation of science. While the original research can be an arduous task, often the culmination of years of work and committment, attemps to reproduce a series of methods to assess if the finding replicates is equally challenging. The researcher must minimally have enough documentation to describe the original data and methods to put together an equivalent experiment, and then use computational methods to look for evidence to assert or reject the original hypothesis. 

Unfortunately, many scientists are not able to provide the minimum product to allow others to reproduce their work. It could be an issue of time - the modern scientist is burdened with writing grants, managing staff, and fighting for tenure. It could be an issue of education. Graduate school training is heavily focused on a particular domain of interest, and developing skills to learn to program, use version control, and test is outside the scope of the program. It might also be entirely infeasible. If the experiments were run on a particular supercomputer and/or with a custom software stack, it is a non trivial task to provide that environment to others. The inability to easily share environments and software serves as a direct threat to scientific reproducibility.

## Encapsulation of Environments with Containers
The idea that the entire software stack, including libraries and specific versions of dependencies, could be put into a container and shared offered promise to help this problem. Linux containers, which can be thought of as encapsulated environments that host their own operating systems, software, and flie contents, were a deal breaker when coming onto the scene in early 2015 [@ARTICLE{Merkel2014-da]. Like Virtual Machines [@BOOK{Smith2005-kg], containers can make it easy to run a newer software stack on an older host, or to package up all the necessary software to run a scientific experiment, and have confidence that when sharing the container, it will run without a hitch. In early 2015, an early player on the scene, an enterprise container solution called Docker, started to be embraced by the scientific community [@MISC{noauthor_2015-ig;@ARTICLE{Ali2016-rh;@ARTICLE{Belmann2015-eb;@ARTICLE{Moreews2015-dy]. Docker containers were ideal for enterprise deployments, but posed huge security hazards if installed on a shared resource.

It wasn't until the introduction of the Singularity software [@Kurtzer2017-x] that these workflows could be securely deployed on local cluster resources. For the first time, scientists could package up all of the software and libraries needed for their research, and deliver a complete package for a second scientist to reproduce the work. Singularity took the high performance computing world by storm, securing several awards and press releases, and within a year being installed at over 45 super computing centers across the globe [@Kurtzer2017-x]. 

## Sharing of Containers for Reproducible Science
Essential to the success of Singularity is not just creation of images, but sharing of them. To address this need, a free cloud service, Singularity Hub [@SingularityHub], was developed by Stanford University Research Computing that offered to build and share containers for scientists. By simply adding a text file named "Singularity" that contained complete instructions for buliding the container to a version controlled Github repository,  the containers were automatically built in the cloud, and immediately accessible via the command line singularity software. A researcher that pushed a recipe on the East Coast would be available to a researcher on the West Coast with a simple "pull" command from the Registry. While this tool was useful to many individual users, unfortunately the setup did not scale to meet the needs of larger institutions. Each Singularity recipe, associated with one container, had to be linked to a Github repository, and to support a large number of users, each user has a quota for the number of builds on the active queue. If an institution wanted to build 1000 containers in a day, a task that would be easy on a scaled cluster, it would not be possible using Singularity Hub. Singularity Hub also ensured its users builds in a standard, protected environment, and allowing users to push images directly to it was out of the question.

Singularity Registry (sregistry) [@SingularityRegistryGithub] was developed to do what Singularity Hub could not - allow an institution or individual to build at scale, and push images that can be private or public to their own hosted registry. Singularity Registry is the first user and institution installable, non-centralized Open Source infrastructure to faciliate the sharing of containers. While Singularity Hub works with cloud builders and object storage,  Singularity Registry is optimized for storage on a local filesystem and any choice of builder (e.g., continuous integration ([Travis](https://www.travis-ci.org), [Circle](https://circleci.com/)), cluster or private node, or separate server). A Registry is also customized with a center's name, and links to appropriate help contacts.

![Singularity Registry Home](registry-home.png)

The Registry, along with native integration into the Singularity software, includes several tools for organization, analysis, and logging of image metrics and usage. Administrators can control the ability for users or the larger community to create accounts, and give finely tuned access (e.g., an expiring token) to share containers. An application programming interface (API) exposes metadata such as container sizes, versioning, and build times. Every time a container is used, or starred by a user, the Registry keeps a record. This kind of metadata not only about containers but about their usage is highly useful to get feedback about highly used containers and general container use. 

Public images are available for programmatic usage for anyone, and private images to authenticated users with the Singularity command line software. Sregistry allows for numerous authentication backends, tracks downloads and starring of images, tagging and versioning, search, and provides an interactive treemap visualization to assess size of image collections relative to one another. 
 
![Singularity Collection Sizes](sizes.png)

Importantly, behind sregistry is a growing and thriving community of scientists, high performance computing (HPC) admins, and research software engineers that are incentivized to generate and share reproducible containers. Complete documentation including setup, deployment, and usage, is available [@SRegistry], and the developers welcome contribution and feedback in any form. Singularity Registry empowers the larger scientific community to build reproducible containers on their cluster or local resource, push them securely to the application, and share them toward transparency and reproducibility for discovery in science.


# References
