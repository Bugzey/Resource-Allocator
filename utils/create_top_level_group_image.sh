#!/bin/bash
if [[ $TOKEN == "" ]]
then
	echo '$TOKEN not found. Run login.sh'
	exit 1
fi

image=$(base64 -w0 "$2")
echo $image

curl -v \
	http://localhost:5000/resource_groups/ \
	-H "Content-Type: application/json" \
	-H "Authorization: Bearer $TOKEN" \
	-d "{\"name\": \"$1\", \"is_top_level\": true, \"image\": {\"image\": \"$image\"}}"
