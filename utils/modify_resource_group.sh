#!/bin/bash
if [[ $TOKEN -eq "" ]]
then
	stop '$TOKEN not found. Run login.sh'
fi

curl -v \
	http://localhost:5000/resource_groups/$1 \
	-X PUT \
	-H "Content-Type: application/json" \
	-H "Authorization: Bearer $TOKEN" \
	-d "{\"name\": \"$2\", \"is_top_level\": $3, \"top_resource_group_id\": $4}"

