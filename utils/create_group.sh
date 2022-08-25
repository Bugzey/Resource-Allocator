#!/bin/bash
#$1 is group name
#$2 is top_level_group
if [[ $TOKEN -eq "" ]]
then
	stop '$TOKEN not found. Run login.sh'
fi

curl -v \
	http://localhost:5000/resource_groups/ \
	-X POST \
	-H "Content-Type: application/json" \
	-H "Authorization: Bearer $TOKEN" \
	-d "{\"name\": \"$1\", \"is_top_level\": false, \"top_resource_group_id\": \"$2\"}"

