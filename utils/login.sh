#!/bin/bash
# $1 - email [default: test@example.com]
# $2 - password [default: 1234Aa!11111]

email=${1:-test@example.com}
password=${2:-1234Aa!11111}

#!/bin/bash
curl -v \
	http://localhost:5000/login/ \
	-X POST \
	-H "Content-Type: application/json" \
	-d "{\"email\": \"$email\", \"password\": \"$password\"}"

