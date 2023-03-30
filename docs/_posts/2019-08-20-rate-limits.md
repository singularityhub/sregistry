---
title:  "Rate Limits Added with 1.1.03"
date:   2019-08-20 01:51:21 -0500
categories: security update
badges:
 - type: info
   tag: security
 - type: success
   tag: update
---

This is an announcement for the 1.0.03 release of Singularity Registry Server!

## Updates

### Collection and Container Limits

We can never anticipate a malicious user making requests to an API or views for a server,
so we've added limits for pulling containers, customizable by the registry.

<!--more-->

### View and API Rate Limits

We've also added [view rate limits](/sregistry/docs/install/settings#view-rate-limits)
and API throttling as another component to customize your registry server. You can be
stringent or flexible in how you allow your users to interact with the server.

### Global Disables

In the case that you need to turn a component off to investigate or debug, we've
added global variables to disabling building, receiving builds, or GitHub webhooks (in
the case of the [Google Build](/sregistry/docs/plugins/google-build) integration.

### Account Control

If users want to delete their account, there is now the the addition of a "Delete Account" button in the User profile
Deleting an account corresponds with deleting all associated containers and collections.

### Private Signed Urls

Previously, we served public containers from Google Storage for the Google Build plugin.
This can be risky if a URL is shared, and then maliciously used to incur charges for
the egress. To better control access, containers are now kept private in storage and accessed via signed urls.
