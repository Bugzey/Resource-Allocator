from python:3.10

copy . .

run pip install --upgrade pip

run pip install .

run pip install gunicorn

expose 5000

entrypoint python -m gunicorn 'resource_allocator.main:create_app()' -b 0.0.0.0:5000
