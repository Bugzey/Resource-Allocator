#!/bin/bash
docker build --tag resource_allocator:latest --no-cache .
docker run --name resource_allocator \
	-e DB_USER\
	-e DB_PASSWORD\
	-e DB_SERVER\
	-e DB_PORT\
	-e DB_DATABASE\
	-e SECRET\
	-e AAD_CLIENT_ID\
	-e AAD_CLIENT_SECRET\
	-e REDIRECT_URI\
	-e TENANT_ID\
	-e SERVER_NAME\
	-e LOCAL_LOGIN_ENABLED \
	--publish 5000:5000 \
	--detach \
	--rm \
	resource_allocator \
