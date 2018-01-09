#!/bin/sh

dind dockerd &
sleep 1
pgrep dockerd > /dev/null || sh -c "echo 'W: Dockerd failed, will not be able to proccess Docker manifests.' >&2"

bootstrap-vz $@
