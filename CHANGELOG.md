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
 - Addition of Google Cloud Build, versioning, tags to collections (1.1.0)
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
