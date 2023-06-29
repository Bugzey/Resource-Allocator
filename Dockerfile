from python:3.10

workdir resource_allocator

copy . .

run pip install --upgrade pip

run pip install .

expose 5000

entrypoint python -m gunicorn 'resource_allocator.main:create_app()' -b 0.0.0.0:5000
