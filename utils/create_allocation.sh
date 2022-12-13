#!/bin/bash
# $1 - iteration_id
# $2 - date
# $3 - user_id
# $4 - source_request_id
# $5 - allocated_resource_id

if [[ $TOKEN == "" ]]
then
	stop '$TOKEN not found. Run login.sh'
fi

curl -v \
	http://localhost:5000/allocation/ \
	-X POST \
	-H "Content-Type: application/json" \
	-H "Authorization: Bearer $TOKEN" \
	-d "{\"iteration_id\": $1, \"date\": \"$2\", \"user_id\": $3, \"source_request_id\": $4, \"allocated_resource_id\": $5}"

