#!/bin/bash

docker buildx build \
	--tag "${CONTAINER_IMAGE:-resource_allocator:latest}" \
	.
