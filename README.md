#	Resource Allocator

##	Description

Resource Allocator is an automated back-end API to facilitate the reservation and allocation of
loosely-defined resources such as desks in an office space. End-users can request a specific
resource or state a combination of preferences that are then used to allocate resources in an
optimal manner. Admin users have the ability to manually allocate resources and to override
automated decisions.

This repository offers a back-end web application programming interface (API) built on the Python
Flask web framework. Data is stored in a relational database. Although PostgreSQL 17 is specifically
targeted, other systems should work directly or be easily integrated.


##	Installation

###	Development

The project is structured as a runnable Python library that can also be built and installed using
pip. Required third-party libraries are available in `requirements.txt`. To install and configure
the application, run the following commands.

Install all requirements. Use of virtual environments is not mandatory:

```
pip install -r requirements.txt
```

One can build and distribute the entire project using `setuptools` and `build` by creating a source
or wheel package:

```
python -m build --wheel
```

Install the package locally:

```
pip install .
```

Running the API requires that environment variables are set up externally and are available both for
development/production use and for running tests. The following variables are mandatory:

Environment variable|Description                                                                             |Default
---                 |---                                                                                     |---
**Authentication**  |                                                                                        |
AAD_CLIENT_ID       |Azure AD application (client) ID                                                        |-
AAD_CLIENT_SECRET   |Azure AD application (client) Secret                                                    |-
REDIRECT_URI        |Redirect URI set in Azure for the app (should be `https://localhost:5000/` when testing)|-
TENANT_ID           |Azure Tenant ID whose registered users can log in                                       |-
LOCAL_LOGIN_ENABLED |Whether local login and registration with username and password is allowed (1,yes,true) |no
**Database**        |                                                                                        |
DB_USER             |Username for connecting to the relational (PostgreSQL) database                         |-
DB_PASSWORD         |Password for connecting to the relational database                                      |-
DB_SERVER           |Database server hostname                                                                |-
DB_PORT             |Database server port                                                                    |5432
DB_DATABASE         |Database (catalog) name to use                                                          |postgres
**App Settings**    |                                                                                        |
ALLOWED_ORIGINS     |Comma-separated list of allowed request origins - for use by web-based front-ends       |-
SECRET              |Long string to use as an application secret for encoding and decoding tokens            |-
SERVER_NAME         |Full URL of the server where `resource_allocator` is deployed                           |-
**Deployment**      |                                                                                        |
CONTAINER_IMAGE     |Name of the container image when building Docker                                        |`resource_allocator:latest`
NUM_WORKERS         |Number of `gunicorn` workers to start when running from `startup.sh`                    |4
PORT                |Port number to serve the application via gunicorn                                       |8000


Local log-ins can be disabled by setting the environment variable `LOCAL_LOGIN_ENABLED` to anything
other than "1", "yes" or "true". If not set, it defaults to "false".

Either all or none of the Azure Active Directory-related variables (AAD_CLIENT_ID,
AAD_CLIENT_SECRET, TENANT_ID, REDIRECT_URI) are required.

The app raises an error if Azure AAD is not set-up and LOCAL_LOGIN_ENABLED is false.

Finally, the application assumes that a schema named `resource_allocator` exists in the database. It
is NOT created when running database migrations.


### Local Deployment

For deploying the server on a local machine, first install all requirements as described above and
then use the provided utility script:

```
bash "utils/deploy_local.sh"
```


### Docker Deployment

To build and then run the server through Docker, run the following script:

```
bash "utils/deploy_docker.sh"
```


##	Usage

To run a development or a low-traffic server, execute the package directly either from the
source directory or after having built and installed a redistributable package:

```
python -m resource_allocator
```

The server can also be run using Flask:

```
flask --app=resource_allocator.main run
```


###	API Endpoints

Several API endpoints are exposed that accept GET, POST, PUT and DELETE HTTP requests.

User registration and authentication:

- Register User:
	- `/register/` - POST

- Login User:
	- `/login/` - POST
	- `/login_azure/` - POST

API Resources:

- Allocation:
	- `/allocation/` - GET, POST
	- `/allocation/<int:id>` - GET, PUT, DELETE
	- `/allocation/automatic_allocation` - POST

- Iteration:
	- `/iterations/` - GET, POST
	- `/iterations/<int:id>` - GET, PUT, DELETE

- Request:
	- `/requests/` - GET, POST
	- `/requests/<int:id>` - GET, PUT, DELETE
	- `/requests/<int:id>/approve` - POST
	- `/requests/<int:id>/decline` - POST

- Resource:
	- `/resources/` - GET, POST
	- `/resources/<int:id>` - GET, PUT, DELETE

- Resource Group:
	- `/resource_groups/` - GET, POST
	- `/resource_groups/<int:id>` - GET, PUT, DELETE

- Resource To Group:
	- `/resource_to_group/` - GET, POST
	- `/resource_to_group/<int:id>` - GET, PUT, DELETE

- Users
    - `/users/` - GET, PUT, DELETE
    - `/users/me` - GET

Example API calls are included in the top-level `utils/` folder using the `curl` command-line
program. Endpoint scripts requiring authentication expect that an environment variable named `TOKEN`
exists. The token can be obtained by registering or logging in a user:

```
bash utils/signup.sh
bash utils/login.sh
```

To use `utils/azure_*` debug scripts, one must also specify a valid user email via the `AZURE_EMAIL`
environment variable.

Some scripts accept ordered command-line arguments that are described in the beginning of the Bash
file.


### Filtering, Sorting and Pagination

All general endpoints in the form `/<item>/` support **filtering, sorting and pagination** to reduce
server load. This is achieved via **query parameters**:

* `limit` - the number of items to return in a single page (min=1, max=200, default=200)
* `page` - the page number to return when there are more than `limit` items returned (min=1)
* `order_by` - field name to order by; use `-<field_name>` for descending order. Multiple `order_by`
  elements can be added separately to the query string
* `filter[<field_name>]` - filter by exact match by a field name. The value provided is an exact
  match. Multiple filters provided in this form are combined in an `AND` operation. `OR` is not
  supported
* `filter[<field_name>][<operation>]` - filter using the given **operation** on the value (or
  comma-separated values) provided. `<operation>` may be one of:

    1. `eq` - equals
    1. `ne` - not equals
    1. `lt` - less than
    1. `le` - less or equal
    1. `gt` - greater than
    1. `ge` - greater or equal
    1. `isin` - equals one of the provided comma-separated values
    1. `notin` - does not equal any of the provided comma-separated values
    1. `like` - partial string match to the provided value (using SQL-style `%` placeholders)

Example calls:

* `GET
  /resources/?limit=10&page=2&order_by=name&order_by=-id&filter[top_resource_group_id]=1&filter[name][notin]=something,other`


### CLI Client

A command-line interface (CLI) client is available for the server in the
[Resource-Allocator-Client](https://github.com/Bugzey/Resource-Allocator-Client) repository.


##	Contributing

Features and bug fixes should be written in their own separate git branches stemming from the head
of the master branch. Automated testing using the `unittest` framework is strongly encouraged.

Existing tests assume an active configuration exists as described in [Installation](#installation),
and that a separate schema called `resource_allocator_test` exists. Tests automatically create, fill
and then delete objects from this schema.

Outstanding features and associated tasks will be tallied in this README file until further notice.

Feature brainstorm:


##	Project Status:

- [ ] Planning
- [ ] Prototype
- [X] In Development
- [ ] In Production
- [ ] Unsupported
- [ ] Retired


##	Authors and Acknowledgement

README based on <https://www.makeareadme.com/>

