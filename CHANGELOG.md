# CHANGELOG

This is a manually generated log to track changes to the repository for each release. 
Each section should include general headers such as **Implemented enhancements** 
and **Merged pull requests**. All closed issued and bug fixes should be 
represented by the pull requests that fixed them. Critical items to know are:

 - renamed commands
 - deprecated / removed commands
 - changed defaults
 - backward incompatible changes


## [master](https://github.com/singularityhub/sregistry/tree/master) (master)
 - Adding container descriptions, editable by owners (1.1.39)
 - fix issues with psycopg2-binary and saml auth (1.1.38)
   - Pin psycopg2-binary 2.8.6 to deal with UTC errors
   - change formatting of the login URL to fix saml auth
 - bump django version update (1.1.37)
 - update base container to Python 3.6.13 (1.1.36)
 - fix google build deprecated djangorestframework function
 - add notes in docs/docker-compose.yaml to pin versions
 - adding GitHub enterprise backend for social auth (1.1.35)
 - remove un-needed lib PyYaml (1.1.34)
 - updating Django and Django Restframework (1.1.33)
 - API endpoint to create a collection (1.1.32)
 - allowing for Bearer token to have any casing (1.1.31)
 - adding minio environment file to https docker-compose (1.1.3)
 - enforcing usernames to be all lowercase (1.1.29)
 - Added ability to specify Minio direct download from interface (1.1.28)
 - Adding cleanup for Minio images no longer referenced in sregistry (1.1.27)
 - Django various updates, version bump 2.2.10 to 2.2.13 (1.1.26)
 - Minio environment needs to be added to scheduler and worker (1.1.25)
 - Adding minio backend for library endpoint (1.1.24)
 - GitHub API is deprecating use of GET parameters, must provide token in header (1.1.23)
 - multipart upload added to scs-library-client, needs to return 404 (1.1.22)
 - fixed bug push of new container (for same tag) does not update binary (1.1.21)
 - adding POSTGRES_HOST_AUTH_METHOD trust to account for changes postgres 9.6.17 (1.1.20)
 - bumping django version to fix two CVEs (1.1.19)
 - pinning verison of Django to not yet upgrade (1.1.18)
 - broken API and documentation links (1.1.17)
 - refactored collections treemap to only show collection container counts (1.1.16)
 - adding logs for cron jobs and fix their execution (1.1.15)
 - black linting and removing default upload_id (1.1.14)
 - push/pull fixes for library API (1.1.13)
 - bug fix with parsing valid token (1.1.12)
 - support for robot users (1.1.11)
 - library endpoint with push/auth (1.1.10)
 - adding key server (1.1.09)
 - fixing bug with select for team permissions (1.1.08)
 - adding backup as cron job (1.1.07)
 - collection settings are viewable by registry staff/superusers (1.1.06)
 - library pull needs to minimally check if container is private (1.1.05)
 - accidental removed of user profile prefix for custom profile (1.1.04)
 - adding django-ratelimit to all views, customized via settings (1.1.03)
   - button in profile to delete account
   - API throttle with defaults for users and anon
 - setting API schema backend to use coreapi.AutoSchema (1.1.02)
 - documentation fixes
 - application migrations added back in run_uwsgi.sh (1.1.01)
   - major update of documentation theme
 - addition of Google Cloud Build, versioning, tags to collections (1.1.0)
 - adding BitBucket authentication backend
 - updating sregistry-cli to 0.0.97, catching OSError earlier
 - updating sregistry-cli to 0.0.96, and Singularity download url to use sylabs organization
 - increasing length of name limit to 500, and catching error (with message and cleanup)
 - adding Globus integration
 - updating sregistry-cli to version 0.0.74
 - superusers and admins (global) can now create collections via a button in the interface
 - demos and customizated supplementary content removed - not used
 - user customization possible by superusers in the admin panel
 - adding teams and basic permissions to view and edit collections
 - changed internal functions to use sregistry client (instead of singularity)
 - authentication check added to sregistry pull, so private images can be pulled given correct credentials
 - updating the token to have format with registry at top level of dictionary (to support other sregistry clients).
 - from the *sregistry client* provided by Singularity Python, to support use of squashfs images and singularity 2.4, the default upload is not compressed, assuming squashfs, and the default download is not decompressed. To still compress an image add the `--compress` flag on push, and the `--decompress` flag on pull.
 - the generation of the date used for the credential has been fixed, done via updating singularity-python.
