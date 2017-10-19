---
layout: registry
title:  "{{ REGISTRY_NAME }}"
base: {{ DOMAIN_NAME }}
date:   {{ DATETIME_NOW }}
author: {{ AUTHOR }}
categories:
- registry
img: robots/robot{{ NUMBER }}.png
thumb: robots/robot{{ NUMBER }}.png # wget https://vsoch.github.io/robots/assets/img/robots/robot15570.png
tagged: {{ REGISTRY_URI }}
institution: {{ REGISTRY_NAME }}
---

{{ REGISTRY_NAME }} is a Singularity Registry to provide institution level Singularity containers.
