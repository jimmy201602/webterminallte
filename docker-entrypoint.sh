#!/bin/sh
set -e

if [ "${1#-}" != "$1" ]; then
       set -- /usr/bin/supervisord -c /etc/supervisord.conf
       set -- /usr/sbin/nginx -c /etc/nginx/nginx.conf
fi

exec "$@"