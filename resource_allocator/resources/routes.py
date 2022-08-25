from resource_allocator.resources.user import RegisterUser, LoginUser
from resource_allocator.resources.resource import (
    ResourceResource, ResourceGroupResource,
)
from resource_allocator.resources.iteration import IterationResource
from resource_allocator.resources.request import RequestResource
from resource_allocator.resources.resource_to_group import ResourceToGroupResource

routes = (
    (RegisterUser, "/register/"),
    (LoginUser, "/login/"),
    (ResourceResource, "/resources/", "/resources/<int:id>"),
    (ResourceGroupResource, "/resource_groups/", "/resource_groups/<int:id>"),
    (ResourceToGroupResource, "/resource_to_group/", "/resource_to_group/<int:id>"),
    (IterationResource, "/iterations/", "/iterations/<int:id>"),
    (RequestResource, "/requests/", "/requests/<int:id>"),
)

