---
layout: default
title: "Installation: Settings"
pdf: true
permalink: /install-settings
toc: false
---

# Settings

See that folder called [settings](https://github.com/singularityhub/sregistry/blob/master/shub/settings)? inside are a bunch of different starting settings for the application. We will change them in these files before we start the application. There are actually only two files you need to poke into, generating a `settings/secrets.py` from our template [settings/dummy_secrets.py](https://github.com/singularityhub/sregistry/blob/master/shub/settings/dummy_secrets.py) for application secrets, and [settings/config.py](https://github.com/singularityhub/sregistry/blob/master/shub/settings/config.py) to configure your database and registry information.


## Secrets
There should be a file called `secrets.py` in the shub settings folder (it won't exist in the repo, you have to make it), in which you will store the application secret and other social login credentials.

An template to work from is provided in the settings folder called `dummy_secrets.py`. You can copy this template:

```bash
cp shub/settings/dummy_secrets.py shub/settings/secrets.py
```

Or, if you prefer a clean secrets file, create a blank one as below:

```bash
touch shub/settings/secrets.py
```

and inside you want to add a `SECRET_KEY`. You can use the [secret key generator](http://www.miniwebtool.com/django-secret-key-generator/) to make a new secret key, and call it `SECRET_KEY` in your `secrets.py` file, like this:

```      
SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```

### Authentication Secrets
One thing I (@vsoch) can't do for you in advance is produce application keys and secrets to give your Registry for each social provider that you want to allow users (and yourself) to login with. We are going to use a framework called [python social auth](https://python-social-auth-docs.readthedocs.io/en/latest/configuration/django.html) to achieve this, and in fact you can add a [number of providers](http://python-social-auth-docs.readthedocs.io/en/latest/backends/index.html) (I have set up a lot of them, including SAML, so please <a href="https://www.github.com/singularityhub/sregistry/isses" target="_blank">submit an issue</a> if you want one added to the base proper.). Singularity Registry uses OAuth2 with a token--> refresh flow because it gives the user power to revoke permission at any point, and is a more modern strategy than storing a database of usernames and passwords. You can enable or disable as many of these that you want, and this is done in the [settings/config.py](https://github.com/singularityhub/sregistry/blob/master/shub/settings/config.py):

```
# Which social auths do you want to use?
ENABLE_GOOGLE_AUTH=False
ENABLE_TWITTER_AUTH=False
ENABLE_GITHUB_AUTH=True
ENABLE_GITLAB_AUTH=False

```

and you will need at least one to log in. I've found that Github works the fastest and easiest, and then Google. Twitter now requires an actual server name and won't work with localost, but if you are deploying on a server with a proper domain go ahead and use it. All avenues are extremely specific with regard to callback urls, so you should be very careful in setting them up. 

Other authentication methods, such as LDAP, are implemented as [plugins](https://singularityhub.github.io/sregistry/plugins/) to sregistry. See the [plugins documentation](https://singularityhub.github.io/sregistry/plugins/) for details on how to configure these.

We will walk through the setup of each in detail. For all of the below, you should put the content in your `secrets.py` under settings. Note that if you are deploying locally, you will need to put localhost (127.0.0.1) as your domain, and Github is now the only one that worked reliably without an actual domain for me.


#### Google OAuth2
You first need to [follow the instructions](https://developers.google.com/identity/protocols/OpenIDConnect) and setup an OAuth2 API credential. The redirect URL should be every variation of having http/https, and www. and not. (Eg, change around http-->https and with and without www.) of `https://www.sregistry.org/complete/google-oauth2/`. Google has good enough debugging that if you get this wrong, it will give you an error message with what is going wrong. You should store the credential in `secrets.py`, along with the complete path to the file for your application:


      GOOGLE_CLIENT_FILE='/code/.grilledcheese.json'

      # http://psa.matiasaguirre.net/docs/backends/google.html?highlight=google
      SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'xxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com'
      SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'xxxxxxxxxxxxxxxxx'
      # The scope is not needed, unless you want to develop something new.
      #SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['https://www.googleapis.com/auth/drive']
      SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
          'access_type': 'offline',
          'approval_prompt': 'auto'
      }


Google is great in letting you specify multiple acceptable callback urls, so you should set every version of `http://127.0.0.1/complete/google-oauth2` (I did with and without http/https, along with the ending and without the ending slash, just in case). Note that `1.` extra arguments have been added to ensure that users can refresh tokens, and `2.` in testing I was using `http` and not `https`, and I eventually added `https` (and so the url was adjusted accordingly). Next, we need to follow instructions for [web applications](https://developers.google.com/identity/protocols/OAuth2WebServer). 

#### Setting up Github OAuth
For users to connect to Github, you need to [register a new application](https://github.com/settings/applications/new), and add the key and secret to your `secrets.py` file like this: 


```
http://psa.matiasaguirre.net/docs/backends/github.html?highlight=github
SOCIAL_AUTH_GITHUB_KEY = ''
SOCIAL_AUTH_GITHUB_SECRET = ''

# You shouldn't actually need this if we aren't using repos
# SOCIAL_AUTH_GITHUB_SCOPE = ["repo","user"]
```

The callback url should be in the format `http://127.0.0.1/complete/github`, and replace the localhost address with your domain. See the [Github Developers](https://github.com/settings/developers) pages to browse more information on the Github APIs.


#### Gitlab OAuth2
Instructions are provided [here](https://github.com/python-social-auth/social-docs/blob/master/docs/backends/gitlab.rst). Basically:

1. You need to [register an application](https://gitlab.com/profile/applications), be sure to add the `read_user` scope. If you need `api`, add it to (you shouldn't).
2. Set the callback URL to `http://registry.domain/complete/gitlab/`. The URL **must** match the value sent. If you are having issues, try adjusting the trailing slash or http/https/. 
3. In your `secrets.py` file under settings, add:

```
SOCIAL_AUTH_GITLAB_SCOPE = ['api', 'read_user']
SOCIAL_AUTH_GITLAB_KEY = ''
SOCIAL_AUTH_GITLAB_SECRET = ''
```
Where the key and secret are replaced by the ones given to you. If you have a private Gitlab, you need to add it's url too:

```
SOCIAL_AUTH_GITLAB_API_URL = 'https://example.com'
```


#### Setting up Twitter OAuth2
You can go to the [Twitter Apps](https://apps.twitter.com/) dashboard, register an app, and add secrets, etc. to your `secrets.py`:

      SOCIAL_AUTH_TWITTER_KEY = ''
      SOCIAL_AUTH_TWITTER_SECRET = ''


Note that Twitter now does not accept localhost urls. Thus, 
the callback url here should be `http://[your-domain]/complete/twitter`.



### Config
In the [config.py](../shub/settings/config.py) you need to define the following:


#### Domain Name
A Singularity Registry Server should have a domain. It's not required, but it makes it much easier for yourself and users to remember the address. The first thing you should do is change the `DOMAIN_NAME_*` variables in your settings [settings/main.py](https://github.com/singularityhub/sregistry/blob/master/shub/settings/main.py).

For local testing, you will want to change `DOMAIN_NAME` and `DOMAIN_NAME_HTTP` to be localhost. Also note that I've set the regular domain name (which should be https) to just http because I don't have https locally:

```
DOMAIN_NAME = "http://127.0.0.1"
DOMAIN_NAME_HTTP = "http://127.0.0.1"
#DOMAIN_NAME = "https://singularity-hub.org"
#DOMAIN_NAME_HTTP = "http://singularity-hub.org"
```

It's up to the deployer to set one up a domain or subdomain for the server. Typically this means going into the hosting account to add the A and CNAME records, and then update the DNS servers. Since every host is a little different, I'll leave this up to you, but [here is how I did it on Google Cloud](https://cloud.google.com/dns/quickstart).


#### Registry Contact
You need to define a registry uri, and different contact information:

```
HELP_CONTACT_EMAIL = 'vsochat@stanford.edu'
HELP_INSTITUTION_SITE = 'srcc.stanford.edu'
REGISTRY_NAME = "Tacosaurus Computing Center"
REGISTRY_URI = "taco"
```

The `HELP_CONTACT_EMAIL` should be an email address that you want your users (and/or visitors to your registry site, if public) to find if they need help. The `HELP_INSTITUTION_SITE` is any online documentation that you want to be found in that same spot. Finally, `REGISTRY_NAME` is the long (human readable with spaces) name for your registry, and `REGISTRY_URI` is a string, all lowercase, 12 or fewer characters to describe your registry.


#### User Collections
By default, any authenticated user in your Registry can create collections, and decide to make them public or private. If you would prefer to revoke this permission (meaning that only administrators can create and manage collections) then you would want to set this variable to `False`.

```
# Allow users to create public collections
USER_COLLECTIONS=True
```

Setting `USER_COLLECTIONS` to False also means that users cannot create [Teams](/sregistry/setup#teams), which are organized groups of users that then can be added as contributors to individual collections. With this setting as True, any authenticated user, staff, or administrator can create and manage new collections and teams, and this is done by issuing a token.


#### Registry Private
By default Singularity Registry will provide public images, with an option to set them to private. If you are working with sensitive data and/or images, you might want all images to be private, with no option to make public. You can control that with the variable `PRIVATE_ONLY`.

```
PRIVATE_ONLY=True
```

The above would eliminate public status and make private the default. Alternatively, if you want to allow for public images but make the default private (and collection owners can make collections of their choice public) set `DEFAULT_PRIVATE` to True.

```
DEFAULT_PRIVATE=True
```

`PRIVATE_ONLY` takes preference to `DEFAULT_PRIVATE`. In other words, if you set `PRIVATE_ONLY` to True, the default has to be private, the change to `DEFAULT_PRIVATE` is meaningless, and a user cannot change a collection to be public.


#### Database
By default, the database itself will be deployed as a postgres image called `db`. You probably don't want this for production (for example, I use a second instance with postgres and a third with a hot backup, but it's an ok solution for a small cluster or single user. Either way, we recommend backing it up every so often.

When your database is set up, you can define it in your `secrets.py` and it will override the Docker image one in the `settings/main.py file`. It should look something like this

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dbname',
        'USER': 'dbusername',
        'PASSWORD':'dbpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### Visualizations
We show a nice treemap as one of the registry tools:

![assets/img/container_treemap.png](assets/img/container_treemap.png)

Also in this file you have the option to "tweak" this threshold of when we go from showing all containers (eg, specific tags) to just containers under collections. If this second approach is still too detailed, we may also make the fallback to just show collections.

```
########################################################################
# Visualizations
########################################################################

# After how many single containers should we switch to showing collections
# only? >= 1000
VISUALIZATION_TREEMAP_COLLECTION_SWITCH=1000
```

#### Logging
By default, Singularity Registry keeps track of all requests to pull containers, and you have control over the level of detail that is kept. If you want to save complete metadata (meaning the full json response for each call) then you should set `LOGGING_SAVE_RESPONSES` to True. If you expect heavy use and want to save the minimal (keep track of which collections are pulled how many times) the reccomendation is to set this to False. 

```
LOGGING_SAVE_RESPONSES=True
```

Great job! Let's now [configure your web server and storage](/sregistry/install-server).
