#!/bin/bash
#

cd /data
pip3 install -r requirements.txt

python3 /data/corvee/manage.py migrate
python3 /data/corvee/manage.py runserver 0.0.0.0:8000
