"""
Main module

This module is the entry point to the appliation crateing and returning a Flask object
"""

from flask import Flask
from flask_restful import Api

from resource_planner.resources.routes import routes

def create_app():
    app = Flask(__app__)
    api = api(app)

    for route in routes::
        api.add_resource(*route)

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

