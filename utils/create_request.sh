#!/bin/bash
# $1 - iteration_id
# $2 - requested_date
# $3 - user_id
# $4 - requested_resource_id
# $5 - requested_resource_group_id

if [[ $TOKEN == "" ]]
then
	stop '$TOKEN not found. Run login.sh'
fi

curl -v \
	http://localhost:5000/requests/ \
	-X POST \
	-H "Content-Type: application/json" \
	-H "Authorization: Bearer $TOKEN" \
	-d "{\"iteration_id\": $1, \"requested_date\": \"$2\", \"user_id\": $3, \"requested_resource_id\": $4, \"requested_resource_group_id\": $5}"

