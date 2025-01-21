FROM postgres:15
RUN apt-get update && apt-get install -y gettext-base && apt-get clean
WORKDIR /docker-entrypoint-initdb.d
COPY init.sql.template /docker-entrypoint-initdb.d/init.sql.template
COPY entrypoint.sh /docker-entrypoint-initdb.d/entrypoint.sh
RUN chmod +x /docker-entrypoint-initdb.d/entrypoint.sh
ENTRYPOINT ["/docker-entrypoint-initdb.d/entrypoint.sh"]
CMD ["postgres"]
