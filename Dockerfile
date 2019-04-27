FROM python:3.7-alpine

# Set the file maintainer (your name - the file's author)
MAINTAINER Ronald Moesbergen

COPY requirements.txt /srv/corvee/requirements.txt

RUN apk update && \
    apk add nginx mariadb-dev zlib-dev gcc musl-dev sqlite && \
    pip3 install --no-cache-dir -r /srv/corvee/requirements.txt && \
    apk del gcc musl-dev

WORKDIR /srv
RUN mkdir static logs /run/nginx

COPY nginx.conf /etc/nginx/nginx.conf

# Port to expose
EXPOSE 80

COPY django/corvee/ /srv/corvee/

# Copy entrypoint script into the image
WORKDIR /srv/corvee
COPY start.sh /
ENTRYPOINT ["/start.sh"]