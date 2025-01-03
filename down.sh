#!/usr/bin/env bash

items=(
    "docker-compose.dev.yml"
    "docker-compose.yml"
)
for item in "${items[@]}" ; do
    echo "[ ${item} ]"
    docker compose -f ${item} down
done
docker network rm shared
