---
title: "Installation: Using Ansible"
pdf: true
toc: true
---

# Installation using Ansible

It is possible to automate the deployment of your Singularity Registry by using Ansible. There is an  Ansible role that can be used for deploying your own [sregistry](https://github.com/singularityhub/sregistry) and installing [sregistry-cli](https://github.com/singularityhub/sregistry-cli). This role is available [here](https://galaxy.ansible.com/grycap/singularity_registry). The documentation could be found [here](https://github.com/grycap/ansible-role-singularity-registry).

For example, if you want to install [sregistry](https://github.com/singularityhub/sregistry) with GitHub and PAM authentication and also the client [sregistry-cli](https://github.com/singularityhub/sregistry-cli), you can create the following ansible playbook:
```yml
- become: true
  hosts: localhost
  vars:
    # Variables to configure GITHUB authorization
    sregistry_secrets_vars:
    - { option: 'SOCIAL_AUTH_GITHUB_KEY', value: "XXXXXXXXXX" }
    - { option: 'SOCIAL_AUTH_GITHUB_SECRET', value: "XXXXXXXXXX" }

    sregistry_config_vars:
      - { option: 'ENABLE_GITHUB_AUTH', value: True }
      - { option: 'HELP_CONTACT_EMAIL', value: 'email@email.com' }
      - { option: 'HELP_INSTITUTION_SITE', value: 'https://www.yourinstitution.com'}
      - { option: 'REGISTRY_NAME', value: 'My Singularity Registry' }
      - { option: 'REGISTRY_URI', value: 'mysreg' }

    # Use PAM authorization
    sregistry_plugins_enabled:
      - pam_auth

    # sregistry-cli in Docker
    sregistry_cli_use_docker: true

  roles:
    - { role: grycap.singularity_registry }
```

Once you completed all the configuration of the role in your recipe, it is time to run the playbook (in this example, it is stored in `sregistry.yml`). It should be pointed out that root privileges are required to install it:
```bash
sudo ansible-playbook sregistry.yml
```
