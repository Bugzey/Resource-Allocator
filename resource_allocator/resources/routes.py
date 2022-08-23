from resource_allocator.resources.user import RegisterUser, LoginUser

routes = (
    (RegisterUser, "/register/"),
    (LoginUser, "/login/"),
)

