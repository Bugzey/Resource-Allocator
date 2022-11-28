#!/bin/bash
if [[ $AZURE_EMAIL -eq "" ]]
then
	stop '$AZURE_EMAIL not found. Configure environment variable'
fi

curl -v \
	http://localhost:5000/login_azure/ \
	-X GET \
	-H "Content-Type: application/json" \

