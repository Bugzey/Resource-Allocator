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


routes = (
    #   Users
    (RegisterUserResource, "/register/"),
    (LoginUserResource, "/login/"),
    (LoginUserAzureResource, "/login_azure/"),
    (UserResource, "/users/", "/users/<int:id>", "/users/me"),

    #   CRUD resources
    (ResourceResource, "/resources/", "/resources/<int:id>"),
    (ResourceGroupResource, "/resource_groups/", "/resource_groups/<int:id>"),
    (ResourceToGroupResource, "/resource_to_group/", "/resource_to_group/<int:id>"),
    (ImageResource, "/images/", "/images/<int:id>"),
    (ImagePropertiesResource, "/image_properties/", "/image_properties/<int:id>"),
    (IterationResource, "/iterations/", "/iterations/<int:id>"),
    (RequestResource, "/requests/", "/requests/<int:id>"),
    (AllocationResource, "/allocation/", "/allocation/<int:id>"),

    #   Convenience Methods
    (AutoAllocationResource, "/allocation/auto_allocation", "/auto_allocation"),
    (RequestApproveResource, "/requests/<int:id>/approve"),
    (RequestDeclineResource, "/requests/<int:id>/decline"),
)
