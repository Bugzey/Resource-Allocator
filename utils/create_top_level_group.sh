#!/bin/bash
if [[ $TOKEN == "" ]]
then
	echo '$TOKEN not found. Run login.sh'
	exit 1
fi

curl -v \
	http://localhost:5000/resource_groups/ \
	-X POST \
	-H "Content-Type: application/json" \
	-H "Authorization: Bearer $TOKEN" \
	-d "{\"name\": \"$1\", \"is_top_level\": true}"

