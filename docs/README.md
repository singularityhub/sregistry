---
layout: default
title: {{ site.name }}
pdf: true
permalink: /
excluded_in_search: true
---

<div style="float:right; margin-bottom:50px; color:#666">
</div>

<div>
    <img src="assets/img/logo.png" style="float:left">
</div><br><br>


# Singularity Registry Server

Hello there! It's so great that you want to use Singularity Registry Server. Let's get started. 

[![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/singularityhub/lobby)
[![DOI](http://joss.theoj.org/papers/10.21105/joss.00426/status.svg)](https://doi.org/10.21105/joss.00426)


### Introduction
This section covers rationale, background, and frequently asked questions.

 - [Introduction](/sregistry/intro): Covers some background and basic information.
 - [Use Cases](/sregistry/use-cases): a few examples of when deploying a Singularity Registry Server is useful
 - [Frequenty Asked Questions](/sregistry/faq): Quick answers to some questions you might have on your mind.

### Deploy a Registry Server
This section is going to cover installation, which means configuration of a Docker image, building of the image, and then starting your image with other services (docker-compose) to run your registry server.

 - [install](/sregistry/install): configure, build, and deploy your registry server.
 - [setup](/sregistry/setup): setting up and registering the running application.
 - [accounts](/sregistry/credentials): User accounts, teams, and credentials for using the client.
 - [plugins](/sregistry/plugins): Details about available plugins, and how to configure them.

### Use a Registry

 - [Interface](/sregistry/interface): interacting with your collections in the interface
 - [sregistry Client](/sregistry/client): The `sregistry-cli` to push, pull, list, and delete.
 - [Singularity Client](/sregistry/client-singularity): A client provided by Singularity natively to pull.


Do you want a new feature? Is something not working as it should? @vsoch wants [your input!](https://www.github.com/singularityhub/sregistry/issues) This registry is driven by desire and need for clusters small and large, so if you don't tell me what you want, how will I know that you want it?

<div>
    <a href="/sregistry/intro"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
