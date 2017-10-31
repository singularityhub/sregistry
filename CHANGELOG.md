# CHANGELOG

This is a manually generated log to track changes to the repository for each release. 
Each section should include general headers such as **Implemented enhancements** 
and **Merged pull requests**. All closed issued and bug fixes should be 
represented by the pull requests that fixed them. This log originated with Singularity 2.4
and changes prior to that are (unfortunately) done retrospectively. Critical items to know are:

 - renamed commands
 - deprecated / removed commands
 - changed defaults
 - backward incompatible changes (recipe file format? image file format?)
 - migration guidance (how to convert images?)
 - changed behaviour (recipe sections work differently)


## [v1.x](https://github.com/singularityhub/singularity-python/tree/development) (development)

**changed defaults**
 - from the *sregistry client* provided by Singularity Python, to support use of squashfs images and singularity 2.4, the default upload is not compressed, assuming squashfs, and the default download is not decompressed. To still compress an image add the `--compress` flag on push, and the `--decompress` flag on pull.

**bugs fixed**
 - the generation of the date used for the credential has been fixed, done via updating singularity-python.
