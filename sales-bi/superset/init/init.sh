#!/bin/bash

CONTAINER_NAME="superset-sales-bi-demo"
FLAG_FILE="/init_done.flag"

if docker exec -it $CONTAINER_NAME sh -c "[ -f $FLAG_FILE ]"; then
  echo "Init script has already been run. Exiting..."
  exit 0
fi

docker exec -it $CONTAINER_NAME superset fab create-admin \
              --username admin \
              --firstname Superset \
              --lastname Admin \
              --email admin@superset.com \
              --password admin

docker exec -it $CONTAINER_NAME superset db upgrade
docker exec -it $CONTAINER_NAME superset init

docker exec -it $CONTAINER_NAME sh -c "touch $FLAG_FILE"