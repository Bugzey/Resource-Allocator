"""
Main module

This module is the entry point to the appliation crateing and returning a Flask object
"""

from flask import Flask, request, Response, abort

from resource_allocator.config import Config
from resource_allocator.resources.allocation import (
    AllocationResource,
    AutoAllocationResource,
)
from resource_allocator.resources.image import (
    ImageResource,
    ImagePropertiesResource,
)
from resource_allocator.resources.iteration import IterationResource
from resource_allocator.resources.request import (
    RequestResource,
    RequestApproveResource,
    RequestDeclineResource,
)
from resource_allocator.resources.resource import (
    ResourceGroupResource,
    ResourceResource,
)
from resource_allocator.resources.resource_to_group import ResourceToGroupResource
from resource_allocator.resources.user import (
    LoginUserResource,
    LoginUserAzureResource,
    RegisterUserResource,
    UserResource,
)


def register_routes(app: Flask, config: Config) -> Flask:
    #   Users
    RegisterUserResource.register_view(app, config, "register", rule="/register/")
    LoginUserResource.register_view(app, config, "login", rule="/login/")
    LoginUserAzureResource.register_view(app, config, "login_azure", rule="/login_azure/")
    UserResource.register_view(app, config, "users")

    #   CRUD resources
    ResourceResource.register_view(app, config, name="resources")
    ResourceGroupResource.register_view(app, config, name="resource_groups")
    ResourceToGroupResource.register_view(app, config, name="resource_to_group")
    ImageResource.register_view(app, config, name="images")
    ImagePropertiesResource.register_view(app, config, name="image_properties")
    IterationResource.register_view(app, config, name="iterations")
    RequestResource.register_view(app, config, name="requests")
    AllocationResource.register_view(app, config, name="allocation")

    #   Convenience Methods
    AutoAllocationResource.register_view(
        app,
        config,
        "allocation_auto_allocation",
        rule="/allocation/auto_allocation",
    )
    AutoAllocationResource.register_view(
        app,
        config,
        "auto_allocation",
        rule="/auto_allocation",
    )
    RequestApproveResource.register_view(
        app,
        config,
        "request_approve",
        rule="/requests/<int:id>/approve",
    )
    RequestDeclineResource.register_view(
        app,
        config,
        "request_decline",
        rule="/requests/<int:id>/decline",
    )


def create_app() -> Flask:
    """
    Flask app factory that also registers API resources

    Args:
        None

    Returns:
        flask.Flask: instantiated Flask application
    """
    config = Config.from_environment()
    app = Flask(__name__)
    register_routes(app, config)

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
    def reset_session(response: Response):
        config.reset_session()
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

        response.headers.add(
            "Access-Control-Allow-Headers",
            ", ".join(["Authorization", "Content-Type"]),
        )
        response.headers.add(
            "Access-Control-Allow-Methods",
            ", ".join(["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH"]),
        )
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
