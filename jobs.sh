#!/usr/bin/env sh

while true; do
  echo "[$(date)] Cleaning old sessions."
  python3 manage.py clearsessions
  echo "[$(date)] Syncing members with central members admin."
  python3 manage.py sync_members
  sleep 3600
done
