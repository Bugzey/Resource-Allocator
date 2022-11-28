#!/bin/bash
# $1 - code

if [[ $AZURE_EMAIL -eq "" ]]
then
	stop '$AZURE_EMAIL not found. Configure environment variable'
fi

curl -v \
	http://localhost:5000/login_azure/ \
	-X POST \
	-H "Content-Type: application/json" \
	-d "{\"email\": \"$AZURE_EMAIL\", \"code\": \"$1\"}"

