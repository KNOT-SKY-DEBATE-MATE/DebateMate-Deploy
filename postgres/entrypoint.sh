#!/bin/bash

set -e

if [[ "$POSTGRES_DEBUG" == "true" ]]; then
  pg_ctl start -D "$PGDATA" -o "-c listen_addresses='localhost'" -w
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    DROP DATABASE IF EXISTS "$POSTGRES_DB";
    CREATE DATABASE "$POSTGRES_DB";
    GRANT ALL PRIVILEGES ON DATABASE "$POSTGRES_DB" TO "$POSTGRES_USER";
EOSQL
  pg_ctl stop -D "$PGDATA" -m fast
fi

envsubst '${POSTGRES_DB} ${POSTGRES_USER} ${POSTGRES_PASSWORD}' \
  < /docker-entrypoint-initdb.d/init.sql.template \
  > /docker-entrypoint-initdb.d/init.sql

exec docker-entrypoint.sh "$@"
