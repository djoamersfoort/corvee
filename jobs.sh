#!/usr/bin/env sh

while true; do
  echo "[$(date)] Cleaning old sessions."
  python3 manage.py clearsessions
  sleep 3600
done
