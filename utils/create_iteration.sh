#!/bin/bash
# $1 is start_date
# $2 is end_date

if [[ $TOKEN -eq "" ]]
then
	stop '$TOKEN not found. Run login.sh'
fi

curl -v \
	http://localhost:5000/iterations/ \
	-X POST \
	-H "Content-Type: application/json" \
	-H "Authorization: Bearer $TOKEN" \
	-d "{\"start_date\": \"$1\", \"end_date\": \"$2\"}"

