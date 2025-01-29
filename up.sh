#!/usr/bin/env bash

items=(
    "docker-compose.yml"
    "docker-compose.dev.yml"
    "docker-compose.ops.yml"
    #"docker-compose.llm.yml"
)

docker network create shared
for item in "${items[@]}" ; do
    echo "[ ${item} ]"
    docker compose -f ${item} up -d --build
done
