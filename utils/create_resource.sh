#!/bin/bash
# $1 is name
# $2 is top_resource_group_id

if [[ $TOKEN == "" ]]
then
	stop '$TOKEN not found. Run login.sh'
fi

curl -v \
	http://localhost:5000/resources/ \
	-X POST \
	-H "Content-Type: application/json" \
	-H "Authorization: Bearer $TOKEN" \
	-d "{\"name\": \"$1\", \"top_resource_group_id\": $2}"

