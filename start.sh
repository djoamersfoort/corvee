#!/bin/sh
#

python3 manage.py migrate                  # Apply database migrations
python3 manage.py collectstatic --noinput  # Collect static files

# Prepare log files and start outputting logs to stdout
touch /srv/logs/gunicorn.log
touch /srv/logs/access.log
tail -n 0 -f /srv/logs/*.log &

# Start nginx
nginx

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn corvee.wsgi:application \
    --name corvee \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --log-level=debug \
    --log-file=/srv/logs/gunicorn.log \
    --access-logfile=/srv/logs/access.log \
    "$@"
