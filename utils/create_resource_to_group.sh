#!/bin/bash
# $1 is resource_id
# $2 is resource_group_id

if [[ $TOKEN -eq "" ]]
then
	stop '$TOKEN not found. Run login.sh'
fi

curl -v \
	http://localhost:5000/resource_to_group/ \
	-X POST \
	-H "Content-Type: application/json" \
	-H "Authorization: Bearer $TOKEN" \
	-d "{\"resource_id\": \"$1\", \"resource_group_id\": $2}"

