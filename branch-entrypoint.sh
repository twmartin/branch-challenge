#!/bin/sh

CONTAINER_ID=$(cat /proc/self/cgroup | grep "docker" | sed s/\\//\\n/g | tail -1)
CONTAINER_JSON=$(curl --unix-socket /var/run/docker.sock localhost/containers/${CONTAINER_ID}/json)

DockerHostname=$(echo ${CONTAINER_JSON} | jq -r '.Config.Hostname')
export DockerHostname

DockerContainerID=$(echo ${CONTAINER_JSON} | jq -r '.Id')
export DockerContainerID

DockerCreated=$(echo ${CONTAINER_JSON} | jq -r '.Created')
export DockerCreated

DockerMacAddress=$(echo ${CONTAINER_JSON} | jq -r '.NetworkSettings.MacAddress')
export DockerMacAddress

DockerIPAddress=$(echo ${CONTAINER_JSON} | jq -r '.NetworkSettings.Networks.bridge.IPAddress')
export DockerIPAddress

DockerImage=$(echo ${CONTAINER_JSON} | jq -r '.Config.Image')
export DockerImage

"/app/main"

exec "$@"
