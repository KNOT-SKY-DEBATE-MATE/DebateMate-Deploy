#!/bin/bash

set -e

envsubst '${POSTGRES_DB} ${POSTGRES_USER} ${POSTGRES_PASSWORD}' \
  < /docker-entrypoint-initdb.d/init.sql.template \
  > /docker-entrypoint-initdb.d/init.sql

exec docker-entrypoint.sh "$@"
