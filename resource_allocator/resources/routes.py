from resource_allocator.resources.user import RegisterUser, LoginUser, LoginUserAzure
from resource_allocator.resources.resource import (
    ResourceResource, ResourceGroupResource,
)
from resource_allocator.resources.iteration import IterationResource
from resource_allocator.resources.request import RequestResource
from resource_allocator.resources.resource_to_group import ResourceToGroupResource
from resource_allocator.resources.allocation import AllocationResource

routes = (
    (RegisterUser, "/register/"),
    (LoginUser, "/login/"),
    (LoginUserAzure, "/login_azure/"),
    (ResourceResource, "/resources/", "/resources/<int:id>"),
    (ResourceGroupResource, "/resource_groups/", "/resource_groups/<int:id>"),
    (ResourceToGroupResource, "/resource_to_group/", "/resource_to_group/<int:id>"),
    (IterationResource, "/iterations/", "/iterations/<int:id>"),
    (RequestResource, "/requests/", "/requests/<int:id>"),
    (AllocationResource,
        "/allocation/",
        "/allocation/<int:id>",
        "/allocation/automatic_allocation"
    ),
)

