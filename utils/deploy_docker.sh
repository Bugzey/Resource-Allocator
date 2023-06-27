#!/bin/bash
if [[ $DB_USER == "" ]]
then
	echo "Necessary environment variables are not set"
	exit 1
fi

docker build --tag resource_allocator:latest .
docker run --name resource_allocator \
	-e DB_USER \
	-e DB_PASSWORD \
	-e DB_HOST \
	-e DB_PORT \
	-e DB_DATABASE \
	-e SECRET \
	-e AAD_CLIENT_ID \
	-e AAD_CLIENT_SECRET \
	-e REDIRECT_URI \
	-e TENANT_ID \
	-e SERVER_NAME \
	-e LOCAL_LOGIN_ENABLED \
	--publish 5000:5000 \
	--rm \
	--detach \
	resource_allocator
