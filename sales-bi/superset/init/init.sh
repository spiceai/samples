#!/bin/bash

docker exec -it superset-sales-bi-demo superset fab create-admin \
              --username admin \
              --firstname Superset \
              --lastname Admin \
              --email admin@superset.com \
              --password admin

docker exec -it superset-sales-bi-demo superset db upgrade
docker exec -it superset-sales-bi-demo superset init
