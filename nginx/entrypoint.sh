#!/bin/bash

if [ ! -f "/etc/letsencrypt/live/${NGINX_CERTBOT_DOMAIN}/fullchain.pem" ]; then
    certbot certonly --standalone --non-interactive --agree-tos --email ${NGINX_CERTBOT_EMAIL} -d ${NGINX_CERTBOT_DOMAIN}
fi

if ! crontab -l | grep -q "certbot renew"; then
    (crontab -l ; echo "0 0 * * * certbot renew --quiet && nginx -s reload") | crontab -
fi

envsubst '${NGINX_SERVER_NAME} ${DJANGO_INTERNAL_PORT} ${WEBSOCKET_INTERNAL_PORT} ${COMPOSE_PROJECT_NAME}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

exec "$@"
