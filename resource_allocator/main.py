"""
Main module

This module is the entry point to the appliation crateing and returning a Flask object
"""

from flask import Flask
from flask_restful import Api

from resource_allocator.config import Config
from resource_allocator.db import get_session
from resource_allocator.resources.routes import routes


def create_app() -> Flask:
    """
    Flask app factory that also registers API resources

    Args:
        None

    Returns:
        flask.Flask: instantiated Flask application
    """
    _ = Config.from_environment()
    sess = get_session()
    app = Flask(__name__)
    api = Api(app)

    for route in routes:
        api.add_resource(*route)

    @app.after_request
    def commit(response):
        sess.commit()
        return response

    return app


def main() -> None:
    """
    Module's main function that is run whenever the module is run on its own from the command line

    Args:
        None

    Returns:
        None
    """
    app = create_app()
    app.run()


if __name__ == "__main__":
    main()
