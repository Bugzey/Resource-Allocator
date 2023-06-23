from python:3.10

run git clone https://github.com/Bugzey/Resource-Allocator.git \
	&& cd Resource-Allocator \
	&& pip install . \
	&& cd ../ \
	&& rm -rf Resource-Allocator/

run pip install gunicorn

expose 5000

entrypoint python -m gunicorn 'resource_allocator.main:create_app()' -b 0.0.0.0:5000
