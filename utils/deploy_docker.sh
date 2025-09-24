#!/bin/bash
if [[ $DB_USER == "" ]]
then
	echo "Necessary environment variables are not set"
	exit 1
fi

echo docker run \
	--name "${CONTAINER_IMAGE:-resource_allocator:latest}" \
	-e AAD_CLIENT_ID \
	-e AAD_CLIENT_SECRET \
	-e REDIRECT_URI \
	-e TENANT_ID \
	-e LOCAL_LOGIN_ENABLED \
	-e DB_USER \
	-e DB_PASSWORD \
	-e DB_HOST \
	-e DB_PORT \
	-e DB_DATABASE \
	-e ALLOWED_ORIGINS \
	-e SECRET \
	-e SERVER_NAME \
	--publish 5000:5000 \
	--detach \
	resource_allocator
