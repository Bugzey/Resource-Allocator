#!/bin/bash
python -m gunicorn \
	"resource_allocator.main:create_app()" \
	-b 0.0.0.0:5000 \
	-w "${NUM_WORKERS:-4}" \
	--access-logfile "-" \
	--error-logfile "-"
