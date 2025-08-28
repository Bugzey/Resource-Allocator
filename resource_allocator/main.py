"""
Main module

This module is the entry point to the appliation crateing and returning a Flask object
"""

from flask import Flask, request, Response, abort
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
    config = Config.from_environment()
    sess = get_session()
    app = Flask(__name__)
    api = Api(app)

    for route in routes:
        api.add_resource(*route)

    @app.before_request
    def check_origin():
        origin = request.headers.get("Origin")
        if origin is None:
            return

        if not config.ALLOWED_ORIGINS:
            abort(400, "No request origins allowed")

        if origin not in config.ALLOWED_ORIGINS:
            abort(400, f"Request origin {origin} not allowed")

    @app.after_request
    def commit(response):
        sess.commit()
        return response

    @app.after_request
    def add_cors(response: Response):
        origin = request.headers.get("Origin")
        if not origin or not config.ALLOWED_ORIGINS:
            return response

        if origin not in config.ALLOWED_ORIGINS:
            #   Error has been handled by check_origin
            return response

        origin = origin if origin in config.ALLOWED_ORIGINS else config.ALLOWED_ORIGINS[0]
        response.headers.add("Access-Control-Allow-Origin", origin)

        allowed_headers = ["Authorization", "Content-Type"]
        response.headers.add("Access-Control-Allow-Headers", ", ".join(allowed_headers))
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
