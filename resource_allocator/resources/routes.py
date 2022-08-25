from resource_allocator.resources.user import RegisterUser, LoginUser
from resource_allocator.resources.resource import (
    ResourceResource, ResourceGroupResource,
)
from resource_allocator.resources.iteration import IterationResource

routes = (
    (RegisterUser, "/register/"),
    (LoginUser, "/login/"),
    (ResourceResource, "/resources/", "/resources/<int:id>"),
    (ResourceGroupResource, "/resource_groups/", "/resource_groups/<int:id>"),
    (IterationResource, "/iterations/", "/iterations/<int:id>"),
)

