#!/bin/bash
if [[ $DB_USER == "" ]]
then
	echo "Necessary environment variables are not set"
	exit 1
fi

echo "Starting server in the background"
nohup python -m gunicorn "resource_allocator.main:create_app()" -b 0.0.0.0:5000 & disown
