# globus-auth - Authentication using Globus

The `globus-auth` plugin allows users to login to sregistry using Globus account information. You
should be familiar with setting up a Globus endpoint on your cluster, and for this installation example we will
walk through setting up a Globus endpoint on your local machine (or the same filesystem where your Registry will be installed).

## How does Singularity Registry work with Globus?
Globus specializes in transfer and permissions. A Singularity Registry specializes in management of of images, and making those images accessible immediately to the Singularity command line tool. Thus, we have the two (somewhat conflicting) needs:

 1. Every image in a registry must have a web accessible URL (https) to be programmatically available to any user of Singularity (given the appropriate permissions for the image). An image provided in a Registry that is connected to Globus but not accessible by a URL is not acceptable.
 2. Globus does not currently support exposing an https address for a file, and even if it did, many Globus endpoints are installed on clusters that do not want or simply cannot allow exposure of these ports. A single cluster that provides a registry with containers closed off to anyone that doesn't have Globus is not acceptable.

Until a solution is implemented that guarantees that any cluster, via the Globus transfer API, can guarantee a web accessible container to a file on a (closed off to world https) we will take a simple approach that, while it doesn't scale, meets the two criteria.

>> Singularity Registry works with Globus by serving its filesystem with images as a Globus endpoint.

This strategy ensures that any image added to the Registry is available via standard Globus APIs but also accessible via an HTTPS address.  More details are discussed below.

### Summary of Plan

 1. The purpose of the registry is to serve images that are accessible via the Singularity command line tool, for anyone using it. Thus, any Globus related content must also have a web-accessible URL (https).
 2. Since https with Globus is under development, the only way for this to be possible is to make the application filesystem a globus directory itself. The images are shared across cluster (with globus) but accessible via Singularity proper with https.
 3. When Globus is able to provide an https address for a cluster image (not sure how this would work for clusters that don't want open ports, it would likely be a proxy for it?) then we can think about having the image storage NOT with the application.

### Updates to the UI
Given that an institution activates the Globus plugin, new to the UI would be:

1. A "subscribe" or "share" button for users/containers applicable. Each image added to the Registry, still with a "push" would thus be shareable.
2. An ability for a registry to subscribe / share all containers with another, and have it done automatically. How does this work?
  - This comes down to permissions for two Globus endpoints
  - Some kind of handshake / agreement has to occur
  - Right now I'm assuming one endpoint being shared with another endpoint coincides with all images/ equivalent permissions   
  - It comes down to a sync, and the sync needs to be hooked up to some kind of ifnotify so that both local and remote registries are updated

3. An ability for a Globus user to subscribe or get a container via Globus, how does it work?
   a. A user would log in with his or her Globus credentials
   b. If a Globus login is detected, the "share" or "subscribe" button is shown
   c. When the user selects to subscribe (should it be a subscribe (e.g., listen for a signal) a get (e.g., one time get) or a share (e.g., make a request?) the Globus API is used. If it's a subscribe, then we need some kind of notification set up, likely with the user's Globus account (not managed by Singularity Registry). If it's a get, then it's a one time transfer. if it's a share, then it's a request (using Globus first) followed by a subscribe.

### Updates to the Server
We are still relatively ok in that the application folder is not being managed by a user, but by the application. Users can then get "read-only" equivalent to the application. However, we need to add in some kind of inotify to be triggered when another registry updates an image (and the file changes) so that the second registry models, etc. are also updated.

We also need to add in another kind of model that (will eventually) support an https (or other external link) for an image. We could either add the model to the current (and an unused field Image.url) and then a local filesystem would have an image file and a remote would have a url, OR create a different kind of container model under the plugin. I'm thinkin the first.

### Views for Plugin
 - A user needs to be able to log in with Globus
 - a default endpoint perhaps should be allowed to be set for the user
 - (is there a different way to set an entire endpoint for an institution?)
 - (how do we manage different levels of permissions under the endpoint? should it happen when a request for transfer happens?)

Interaction with the registry works as follows:

1. As it does now, with an admin pushing. However, the push sees that the Globus folder is enabled, and a "share" button (or similar) is added.

## Limitations
Ideally, if a Globus image on a filesystem external to where the Registry is served can still be accessible via https, then a single registry is much more scalable in allowing for many disparate file systems (and thus a larger storage). It also helps that downloads / general bandwidth isn't the responsibility of one server.


## Endpoint Setup
We will be following the instructions to set up a [globus connect personal](https://www.globus.org/globus-connect-personal) that will serve the Registry, specifically using the linux [instructions for the command line](https://docs.globus.org/how-to/globus-connect-personal-linux/#globus-connect-personal-cli). For me, that looked something like the following:

```
wget https://s3.amazonaws.com/connect.globusonline.org/linux/stable/globusconnectpersonal-latest.tgz
cd /home/vanessa/Documents/
tar xzf /home/vanessa/Downloads/globusconnectpersonal-latest.tgz 
cd globusconnectpersonal-2.3.3/
```

The documentation doesn't do a good job to mention it, but the next command requires installing the [globus client](https://docs.globus.org/cli/installation/):

```
pip install globus-cli

# check install 
which globus

# login
globus login
```

After the above you should have a browser window open up to log you into the client. Then you can proceed with creating a personal endpoint. It comes down to generating a named endpoint and key, and then running a command to set it up:

```
globus endpoint create --personal my-linux-laptop
./globusconnectpersonal -setup <setup-key>

# search for your newly created endpoint
globus endpoint search --filter-scope my-endpoints
```

I wanted to limit what was under the endpoint since the entire of my home scared me, so I opened this file:

```
vim ~/.globusonline/lta/config-paths
```

and changed the following:

```
~/,0,1
#to
~/Documents/Globus/,0,1
```

Then start your endpoint, and see metadata about it:

```
./globusconnectpersonal -start &
globus ls <endpoint_id>
```

However, we would actually want to limit our endpoint to be a folder that is seen by the application, specifically the same folder that our application uses to store images. For our container, this is mounted at "images" and we want it to be read only:

```
~/Documents/Dropbox/Code/sregistry/sregistry/images,0,0
```

You would want to stop and start the endpoint after this change:

```
./globusconnectpersonal -stop
./globusconnectpersonal -start &
```

**QUESTION** It seems that the full path of an endpoint is always shown, and I'd prefer the user to just see it from the root. Is this possible?


## Globus Configuration
At this point, we have an image folder local to the application also configured as a Globus Endpoint. Next, we want to edit the configuration of our application to enable logging in with globus authentication, and generate a client.

To enable Globus authentication you must:

  * Uncomment the Dockerfile section to install Globus dependencies *before* building the image
  * Add `globus_auth` to the `PLUGINS_ENABLED` list in `shub/settings/config.py`

Then [follow the steps](http://globus-sdk-python.readthedocs.io/en/stable/tutorial/#step-1-get-a-client) to generate a client. Add your client id to the `settings/secrets.py` as `GLOBUS_CLIENT_ID`.

  * Configure the details of your Globus shared directory in `shub/settings/secrets.py`. See
    `shub/settings/dummy_secrets.py` for an example configuration. A good start is to do the following:

```
cp shub/settings/dummy_secrets.py shub/settings/secrets.py
```

Stopped here... working on login.

## ToDos
0. Finish login and instructions for making local globus endpoint?
1. Add login /auth page using globus-sdk
1. how images are mapped to local globus ldap. Is it for a user? a cluster? I think it would make sense for a cluster (and then users just do singularity pull).
2. Should single images be requested / shared, or entire directories?
3. Should the share be automaitc, or manual? In both cases, how is the model created?
4. Why would I want globus over just singularity pull?
5. How does Globus make sense for an application running on a server that isn't a part of the cluster?

## Plan

1. The purpose of the registry is to serve images that are accessible via the singularity command line tool, for anyone using it. Thus, any Globus related content must also have a web-accessible URL (https).
2. Since https with globus is under development, the only way for this to be possible is to make the application filesystem a globus directory itself. The images are shared across cluster (with globus) but accessible via Singularity proper with https.
3. When Globus is able to provide an https address for a cluster image (not sure how this would work for clusters that don't want open ports, it would likely be a proxy for it?) then we can think about having the image storage NOT with the application.

New to the UI would be:

1. A "subscribe" or "share" button for users/containers applicable
2. An ability for a registry to subscribe / share all containers with another, and have it done automatically**
  - This comes down to permissions for two Globus endpoints
  - Some kind of handshake / agreement has to occur
  - Right now I'm assuming one endpoint being shared with another endpoint coincides with all images/ equivalent permissions

Interaction with the registry works as follows:

1. As it does now, with an admin pushing. However, the push sees that the Globus folder is enabled, and a "share" button (or similar) is added.

[..back](../README.md)
