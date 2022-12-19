#!/bin/bash
# $1 - email [default: test@example.com]
# $2 - password [default: 1234Aa!11111]

email=${1:-test@example.com}
password=${2:-1234Aa!11111}

curl -v \
	http://localhost:5000/register/ \
	-X POST \
	-H "Content-Type: application/json" \
	-d "{\"email\": \"$email\", \"password\": \"$password\", \"first_name\": \"test\", \"last_name\": \"test\"}"

