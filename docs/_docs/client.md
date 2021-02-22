---
title: Singularity Clients
pdf: true
toc: false
---

# Singularity

## Singularity Pull

Singularity Registry Server implements a basic version of the Sylabs Library API, 
meaning that you can pull a container with Singularity directly. 

**Important** you must be using Singularity 3.3.0 or greater for this to work! 
If not, you should use [Singularity Registry Client](#singularity-registry-client)
 (which also has examples below of using the `shub://` endpoint with singularity).

For example, let's say that I have a collection with a container called `collection/container:tag`. and my registry is served at `containers.page`. I could pull it as follows:

```bash
$ singularity pull --library https://containers.page collection/container:tag
```

You can also pull a container using Singularity natively with the `shub://` uri:

```bash
$ singularity pull shub://containers.page/collection/container:tag
```

## Singularity Push

As of version `1.1.10`, Singularity Registry Server offers a library endpoint
to authenticate and then push containers. First, create an endpoint for your
registry:

```bash
$ singularity remote add --no-login DinosaurCloud cloud.dinosaur.io
```

Verify it's there:

```bash
$ singularity remote list
NAME           URI              	GLOBAL
DinosaurCloud  cloud.dinosaur.io        NO
[SylabsCloud]  cloud.sylabs.io   	YES
```

**Important** Sylabs requires these endpoints to have https, for obvious reasons. If you want to test with localhost, you'll need to edit [this file](https://github.com/sylabs/singularity/blob/5e483be4af2e120e646d33f0757e855c8d3be2da/internal/pkg/remote/remote.go#L237)
and re-compile Singularity to set the url to have http. The example above is a hypothetical "cloud.dinosaur.io" however in actual development, I used 127.0.0.1 (and you'll see it 
in various spots below). This is how I developed this set of endpoints.

Once you add the remote, then you'll first need to login and get your token at the /token endpoint, for example:

```bash
1eb5bc1daeca0f5a215ec242c9690209ca0b3d71
```

And then provide it (via copy paste) to the Singularity client to create a remote endpoint for your registry:

```bash
$ singularity remote login DinosaurCloud
INFO:    Authenticating with remote: DinosaurCloud
Generate an API Key at https://127.0.0.1/auth/tokens, and paste here:
API Key: 
INFO:    API Key Verified!
```

If you paste a token that isn't valid, you'll get a different message

```bash
$ singularity remote login DinosaurCloud
INFO:    Authenticating with remote: DinosaurCloud
Generate an API Key at https://127.0.0.1/auth/tokens, and paste here:
API Key: 
FATAL:   while verifying token: error response from server: Invalid Token
```

In case you are wondering, the token is kept in plaintext at `/home/vanessa/.singularity/remote.yaml`
so once you specify to use an endpoint, it knows the token. If you are having
issues copy pasting the token into your terminal (I had some when I wanted to
re-create it) you can also just open up this file and edit the text manually:

```
$ cat /home/vanessa/.singularity/remote.yaml Active: DinosaurCloud
Remotes:
  DinosaurCloud:
    URI: 127.0.0.1
    Token: 1eb5bcrdaeca0f5a215ef242c9690209ca0b3d71
    System: false
  SylabsCloud:
    URI: cloud.sylabs.io
    Token: hahhaayeahrightdude
    System: true
```

The easiest thing to do is now to set your remote to be DinosaurCloud (or whatever
you called it) so you don't need to specify the push command with `--library`:

```bash
singularity remote use DinosaurCloud
```

Now that we have a token, let's try a push! For security purposes, the collection
should already exist, and be owned by you. Collaborators are not allowed to push.

```bash 
                                         # library://user/collection/container[:tag]
$ singularity push -U busybox_latest.sif library://vsoch/dinosaur-collection/another:latest
```

If you don't do "remote use" then you can specify the library on the fly:

```bash
$ singularity push -U --library http://127.0.0.1 busybox_latest.sif library://vsoch/dinosaur-collection/another:latest
WARNING: Skipping container verifying
INFO:    http://127.0.0.1
INFO:    0a4cb168d3dabc3c21a15476be7f4a90396bc2c1
INFO:    library://vsoch/dinosaur-collection/another:latest
INFO:    [latest]
 656.93 KiB / 656.93 KiB [===================================================================] 100.00% 15.36 MiB/s 0s
```

We use `-U` for unsigned.

### Push Logic

 - If you push an image to a non existing collection, the collection will be created first (version `1.1.32`)
 - If you push an image to a non existing container, the container will be created first (version `1.1.33`) (\*)
 - If you push a new image, it will be added.
 - If you push a new tag, it will be added.
 - If you push an existing tag, if the container is unfrozen, it will be replaced
 - If you push an existing tag and the container is frozen (akin to protected) you'll get permission denied.

(\*) The Singularity Registry Server data model is different from this of Sylabs library. In the former, a container is created from an image. In the latter, containers are just placeholders for images with the same name, and can be empty. Hence Singularity Registry Server just [mimics the container creation without actually doing it](#mimic-empty-container-creation). The container is created afterwards at the upload step.

### Push Size

The push (as of this version) can now handle large images! Here is the largest that I've tested:

```bash
$ singularity push -U rustarok_latest.sif library://vsoch/dinosaur-collection/rustarok:latest
WARNING: Skipping container verifying
INFO:    http://127.0.0.1
INFO:    0a4cb168d3dabc3c21a15476be7f4a90396bc2c1
INFO:    library://vsoch/dinosaur-collection/rustarok:latest
INFO:    [latest]
 8.09 GiB / 8.09 GiB [====================================================================] 100.00% 91.31 MiB/s 1m30s
```

Of course, do this at your own risk! That is a *CHONKER*!

<hr>
<br>

# Singularity Registry Client

Singularity Registry Global Client, or [sregistry-cli](https://github.com/singularityhub/sregistry-cli),
is a general client to interact with Singularity images at remote endpoints, and it provides
such an endpoint for Singularity Registry Server. We will provide
basic instructions here, and for the full documentation, please see the [getting started guide here](https://singularityhub.github.io/sregistry-cli/client-registry). Note that you will need to [export your credentials](https://singularityhub.github.io/sregistry/credentials) in order to have authenticated interaction with sregistry.


## Install

### sregistry Installation

`sregistry` is the client for Singularity Registry server. To install, you can do the following:

```bash
git clone https://github.com/singularityhub/sregistry-cli
cd sregistry-cli
python setup.py install
```

To check your install, run this command to make sure the `sregistry` client is found.

which sregistry


### Container Install

We have provided a Singularity build definition for you, for which you can use to build a container that serves as the sregistry client (and this will likely be provided on Singularity Hub so you don't even need to do that.) To build, do the following:

```bash
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

```bash
sregistry pull banana/pudding:milkshake
Progress |===================================| 100.0% 
Success! banana-pudding-milkshake.img
```

This is useful so that you can (locally from your registry) pull an image without needing to specify the registry url. It's also important because registry support will only be added to Singularity when the entire suite of compoenents are ready to go!


### Push

If you don't have an image handy, you can pull one from Singularity Hub:

```bash
singularity pull shub://vsoch/hello-world
```

And then a push to your registry looks like this:

```bash
sregistry push vsoch-hello-world-master.img --name dinosaur/avocado --tag delicious
sregistry push vsoch-hello-world-master.img --name meowmeow/avocado --tag nomnomnom
sregistry push vsoch-hello-world-master.img --name dinosaur/avocado --tag whatinthe
```

If you don't specify a tag, `latest` is used. If you have authentication issues,
remember that you need to [export a token](https://singularityhub.github.io/sregistry/credentials) for your user, and ensure that the user is either an admin/manager, or
that you have set the `USER_COLLECTIONS` variable to true. You can read [more about roles here](https://singularityhub.github.io/sregistry/setup-roles), and [more about teams](https://singularityhub.github.io/sregistry/setup-teams) to manage groups of people.

### List

List is a general command that will show a specific container, a specific collection, optionally with a tag. Examples are provided below:

```bash
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

```bash
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

```bash
sregistry delete dinosaur/tacos:delicious
sregistry list
```

if you want to force it, add `--force`

```bash
sregistry delete dinosaur/tacos:delicious --force
```

### Labels
Labels are important, and so they are represented as objects in the database for index, query, etc. Akin to containers, we can list and search:

```bash
# All labels
sregistry labels

# A specific key
sregistry labels --key maintainer

# A specific value
sregistry labels --value vanessasaur

# A specific key and value
sregistry labels --key maintainer --value vanessasaur
```

# Curl

Like with the Sylabs Library API, it is possible to interact with Singularity Registry Server 
using Curl. You can browse the API schema via the `/api` path of your server.

## Authentication

Authentication is done presenting the token in an `Authorization` header:

```bash
$ curl -s -H 'Authorization: Bearer <token>' http://127.0.0.1/<api_endpoint>
```

The token can be found in the navigation in the top right of the registry interface
after you log in.

## Create a collection

As of version `1.1.32` it is possible to create a new collection via the API. It requires authentication.
First retrieve the numeric `id` associated with your username with a GET request to the endpoint `/v1/entities/<username>`.

```bash
$ curl -s -H 'Authorization: Bearer <token>' http://127.0.0.1/v1/entities/<username>
```
Here is a response made pretty by piping into json_pp:
```
{
   "data" : {
      "collections" : [],
      "createdAt" : "2021-02-21T05:20:18.454003Z",
      "createdBy" : "",
      "customData" : "",
      "defaultPrivate" : false,
      "deleted" : false,
      "deletedAt" : "0001-01-01T00:00:00Z",
      "description" : "vsoch",
      "id" : "1",
      "name" : "vsoch",
      "quota" : 0,
      "size" : 0,
      "updatedAt" : "2021-02-21T05:20:18.479251Z",
      "updatedBy" : ""
   }
}
```

Notice that the id is 1? Great! We will use this to create a collection. We next issue
a POST request to the endpoint `/v1/collections` and this json payload:

```
{
  "entity": "<user_numeric_id>"
  "name": "<new_collection_name>"
  "private": true|false
}
```

Here is an example with our user id of 1:

```bash
$ curl -X POST -H 'Authorization: Bearer <token>' -H "Content-Type: application/json" --data '{"entity": 1, "name": "dinosaurs"}' http://127.0.0.1/v1/collections 
```

You can then see the response that the collection was created, and it will appear in the interface:

```bash
{
   "data" : {
      "containers" : [],
      "createdAt" : "2021-02-21T05:35:36.491446Z",
      "createdBy" : "1",
      "customData" : "",
      "deleted" : false,
      "deletedAt" : "0001-01-01T00:00:00Z",
      "description" : "Dinosaurs Collection",
      "entity" : "1",
      "entityName" : "vsoch",
      "id" : "2",
      "name" : "dinosaurs",
      "owner" : "1",
      "private" : false,
      "size" : 0,
      "updatedAt" : "2021-02-21T05:35:36.505902Z",
      "updatedBy" : "1"
   }
}
```

The `private` key is optional. If not provided, it defaults to the servers's configured default for collection creation.
In case of a `singularity push` to a non existing collection, the client triggers the collection creation first, using this endpoint, then pushes the image.

## Mimic empty container creation

As of version `1.1.33` it is possible to mimic the Sylabs library endpoint for new container creation. It requires authentication.

First retrieve the numeric `id` associated with the holding collection with a GET request to the endpoint `/v1/collections/<entity>/<collection_name>`, where `<entity>` is your username.

```bash
$ curl -s -H 'Authorization: Bearer <token>' http://127.0.0.1/v1/collections/<entity>/<collection_name>
```

This is the value associated with the `id` key of the answer. For example:
```
{
  "data": {
    "deletedAt": "0001-01-01T00:00:00Z",
    "entityName": "pini",
    "deleted": false,
    "name": "pini-private",
    "owner": "1",
    "size": 4,
    "description": "My private collection",
    "customData": "",
    "entity": "1",
    "updatedBy": "1",
    "id": "6",
    "createdBy": "1",
    "private": true,
    "createdAt": "2021-02-20T20:21:13.692215Z",
    "containers": [
      "5",
      "6",
      "7",
      "8"
    ],
    "updatedAt": "2021-02-20T20:21:13.777940Z"
  }
}
```

Then we can issue a POST request to the endpoint `/v1/containers` with the payload:
```
{
  "collection": "<collection_numeric_id>"
  "name": "<new_container_name>"
}
```
```bash
$ curl -X POST -H 'Authorization: Bearer <token>' -H "Content-Type: application/json" --data '{"collection": 6, "name": "fish"}' http://127.0.0.1/v1/containers 
```

There is no container creation, because it is not needed with the Singularity Registry Server data model. But the response is as if the container was created so that any workflow using this endpoint could work the same as with Sylabs library:

```bash
{
  "data": {
    "collection": "6",
    "description": "My private collection",
    "collectionName": "pini-private",
    "owner": "1",
    "readOnly": false,
    "id": "6",
    "size": 4,
    "imageTags": {},
    "createdBy": "1",
    "private": true,
    "downloadCount": null,
    "updatedAt": "2021-02-20T20:21:13.777940Z",
    "fullDescription": "Test-private Collection",
    "deletedAt": "0001-01-01T00:00:00Z",
    "entityName": "pini",
    "deleted": false,
    "name": "test-private",
    "stars": 0,
    "customData": "",
    "images": [],
    "entity": "1",
    "updatedBy": "1",
    "archTags": {
      "amd64": {}
    },
    "createdAt": "2021-02-20T20:21:13.692215Z",
    "containers": [
      "5",
      "6",
      "7",
      "8"
    ]
  }
}
```
