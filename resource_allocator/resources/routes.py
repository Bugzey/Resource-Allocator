from resource_allocator.resources.user import RegisterUser, LoginUser
from resource_allocator.resources.resource import ResourceResource

routes = (
    (RegisterUser, "/register/"),
    (LoginUser, "/login/"),
    (ResourceResource, "/resources/", "/resources/<int:id>"),
)

