"""
Startup file in case gunicorn fails to load the project
"""
import logging
import os
import sys

from flask import Flask


logger = logging.getLogger("resource_allocator")
logger.setLevel(logging.INFO)

error = None


try:
    from resource_allocator.main import create_app
    app = create_app()
except ImportError as e:
    error = e
    logger.error(f"Error importing resource_allocator: {e}")
    logger.info(f"Contents: {os.listdir()}")
    logger.info(f"Sys.path: {sys.path}")
    app = Flask(__name__)

    @app.route("/")
    def index():
        return f"""
        Error loading full appilcation: {error}

        Directory: {os.listdir()}

        Sys.path: {sys.path}"""
