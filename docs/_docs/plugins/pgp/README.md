---
title: "pgp keystore"
pdf: true
toc: false
permalink: docs/plugins/pgp
---

# PGP KeyStore

The `pgp` plugin adds necessary endpoints for your Singularity Registry server to store
and interact with keys. It uses the [OpenPGP Server](https://tools.ietf.org/html/draft-shaw-openpgp-hkp-00)
protocol, meaning that activating the plugin will expose "lookup" and "add" endpoints.

To enable the pgp plugin you must:

  * Add `pgp` to the `PLUGINS_ENABLED` list in `shub/settings/config.py`
  * Build the docker image with the build argument ENABLE_PGP set to true:
    ```bash
    $ docker build --build-arg ENABLE_PGP=true -t quay.io/vanessa/sregistry .
    ```

The keystore, unlike other plugins, requires no further setup. Brief interactions
for usage are shown below.
  
## Quick Start

Singularity has it's own little key storage in your home, at `$HOME/.singularity/sypgp`. It also
has a set of client functions, `singularity key` to interact with local and remote keys. 
For the client commands we will be using this client.

**Important**: If you are deploying a server, you are required to have https for the
Sylabs Singularity client to interact with the keystore to work. if you don't,
you will see this message:

```
ERROR: push failed: TLS required when auth token provided
```

You can either secure your server with https, or you can test using localhost,
which will work without TLS.

### 1. Create a Key

The first thing that you want to do is likely to create a local key. Again, all of these
interactions from the client side will use the Singularity software.

```bash
$ singularity key newpair
```

Follow the prompts to generate a key, and don't choose yes to send to sylabs cloud (unless you want to).

### 2. List Keys

When you finish, you should be able to list the key:

```bash
$ singularity key list
Public key listing (/home/vanessa/.singularity/sypgp/pgp-public):

0) U: Vanessasaurus (dinosaurs) <vsochat@stanford.edu>
   C: 2019-10-01 12:23:48 -0400 EDT
   F: CFA6763B11637E52404A25F5DE565315F5198C71
   L: 4096
   --------
```

Note that I chose "dinosaurs" as a keyword so it would be searchable by that. The long string (F)
is the unique id.

### 3. Push Key

Now that we have a key, and we know it's identifier, let's push it to our registry server!
For the example below, we have the server running at http://localhost.
This command is exactly as you would do with Singularity, but we need to provide an additional `--url`
to designate the server base.

```bash
$ singularity key push --url http://localhost CFA6763B11637E52404A25F5DE565315F5198C71
public key `CFA6763B11637E52404A25F5DE565315F5198C71' pushed to server successfully
```

### 4. Search for Key

First you can try searching and providing the URL - and I'm not actually sure if this searches locally and remote, but you see the result:

```bash
$ singularity key search --url http://localhost  dinosaur
Showing 1 results

KEY ID    BITS  NAME/EMAIL
f5198c71  4096  Vanessasaurus (dinosaurs) <vsochat@stanford.edu>  

```

Let's delete all of our local keys to verify that we are really searching the Singularity Registry Server:

```bash
$ rm /home/vanessa/.singularity/sypgp/pgp-public 
```

Now let's do the search again. Since it still shows up, it must be from the registry!

```bash
$ singularity key search --url http://localhost  dinosaur
Showing 1 results

KEY ID    BITS  NAME/EMAIL
f5198c71  4096  Vanessasaurus (dinosaurs) <vsochat@stanford.edu>  
```

Now pull it! We can see that 1 key is added.

```bash
$ singularity key pull --url http://localhost CFA6763B11637E52404A25F5DE565315F5198C71
1 key(s) added to keyring of trust /home/vanessa/.singularity/sypgp/pgp-public
```

If you had tried to add the key without deleting the local one first, you already would have had it 
(note below that zero keys are added):

```bash
$ singularity key pull --url http://localhost CFA6763B11637E52404A25F5DE565315F5198C71
0 key(s) added to keyring of trust /home/vanessa/.singularity/sypgp/pgp-public
```
