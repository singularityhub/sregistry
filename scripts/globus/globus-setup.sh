#!/bin/bash

# This script configures the endpoint, to be done interactively after install

ROBOTNAME=$(python /code/scripts/globus/robotnamer.py)
ENDPOINT="sregistry-${ROBOTNAME}"
export ROBOTNAME ENDPOINT

# Bug with getting $USER, see https://github.com/globus/globus-cli/issues/394

export USER="tunel-user"

if [ ! -f "$HOME/.globus.cfg" ]; then
    echo "Logging in to Globus"
    globus login --no-local-server
fi

echo "Generating Globus Personal Endpoint"
token=$(globus endpoint create --personal "${ENDPOINT}" --jmespath 'globus_connect_setup_key'  | tr -d '"') 
/opt/globus/globusconnectpersonal -setup "${token}"

# Export that globus plugin is enabled to config

if ! grep -q \"globus\" /code/shub/settings/config.py; then
    echo "PLUGINS_ENABLED+=[\"globus\"]" >> /code/shub/settings/config.py
fi

# Even if we already have a previous robot name, it must correspond
# to naming of this endpoint, so we re-generate (and get a new log file)
echo "ROBOTNAME='${ROBOTNAME}'" >> /code/shub/settings/config.py

ENDPOINT_ID=$(globus endpoint local-id)
if [ "${ENDPOINT_ID}" != "No Globus Connect Personal installation found." ]; then
    echo "PLUGIN_GLOBUS_ENDPOINT=\"${ENDPOINT_ID}\"" >> /code/shub/settings/config.py
fi    

# Have we set up config paths yet?
if [ ! -f "$HOME/.globusonline/lta/config-paths" ]; then
    mkdir -p "${HOME}/.globusonline/lta"
    cp /code/scripts/globus/config-paths "${HOME}/.globusonline/lta/config-paths";
fi
