#!/bin/bash

mkdir -p /dontbudge/db
mkdir -p /dontbudge/logs
touch /dontbudge/logs/error.log
touch /dontbudge/logs/access.log

exec gunicorn --workers 4 --bind 0.0.0.0:9876 --log-level=info --log-file=/dontbudge/logs/error.log --access-logfile=/dontbudge/logs/access.log run:app