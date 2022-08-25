#	Resource Planner

##	Description
Resource planner is an automated back-end API to facilitate the reservation and allocation of
loosely-defined resources such as desks in an office space. End-users can request a specific
resource or state a combination of preferences that are then used to allocate resources in an
optimal manner. Admin users have the ability to manually allocate resources and to override
automated decisions.

This repository offers a back-end web application programming interface (API) built on the Python
Flask web framework. Data is stored in a relational database. Although PostgreSQL 14 is specifically
targeted, other systems should work directly or be easily integrated.


##	Installation
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

Running the API requires that environment variables are set up externally and are available both for
development/production use and for running tests. The following variables are mandatory:

|Environment variable|Description|
|---|---|
|USER|Username for connecting to the relational (PostgreSQL) database|
|PASSWORD|Password for connecting to the relational database|
|SERVER|Database server hostname|
|PORT|Database server port|
|DATABASE|Database (catalog) name to use|
|SECRET|Long string to use as an application secret for encoding and decoding tokens|

Furthermore, the application assumes that a schema named `resource_allocator` exists in the
database. It is NOT created when running database migrations.


##	Usage
###	Starting the Server
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

- Register User:
	- `/register/`
- Login User:
	- `/login/`
- Resource:
	- `/resources/`
	- `/resources/<int:id>`
- Resource Group:
	- `/resource_groups/`
	- `/resource_groups/<int:id>`
- Resource To Group:
	- `/resource_to_group/`
	- `/resource_to_group/<int:id>`
- Iteration:
	- `/iterations/`
	- `/iterations/<int:id>`
- Request:
	- `/requests/`
	- `/requests/<int:id>`
- Allocation:
	- `/allocation/`
	- `/allocation/<int:id>`
	- `/allocation/automatic_allocation`


##	Contributing
Features and bug fixes should be written in their own separate git branches stemming from the head
of the master branch. Automated testing using the `unittest` framework is strongly encouraged.

Existing tests assume an active configuration exists as described in [Installation](#installation),
and that a separate schema called `resource_allocator_test` exists. Tests automatically create, fill
and then delete objects from this schema.

Outstanding features and associated tasks will be tallied in this README file until further notice.

Feature brainstorm:

* [ ] database objects
	* [X] user
	* [X] resource
	* [X] resource group (can be recursive)
	* [X] iteration - type of time iteration to request resources for (?)
	* [X] request - pending user requests
	* [X] resource to group - many-to-many mapping
	* [ ] allocation - resource X user X iteration X exact date

* [ ] endpoints:
	* [ ] /users/ - list all users (admin required)
	* [X] /resource/ - list all resources
	* [X] /resource_group/ - (?)
	* [X] /iteration/ - create, list
	* [X] /request/ - post a request for a resource
	* [X] /resource_to_group/ - many-to-many mapping
	* [X] /allocation/ - start the automatic allocation, be able to pass overrides

* [X] allocation algorithm - initial + partial addition?
	* [ ] apply overrides without question
	* [X] distribute weights according to request preferences - each user has 10 points
	* [ ] assign an additional 2 points to history - if the person is assigned to the previous
	  last resource they used or were assigned to
	* [X] Use simplex algorithm? Alternatively try to sort days by possible preference points
	  (getting combinatorical here)

* [ ] Third-party integration
	* [ ] Optional log-in via Azure Active Directory (AD) for a specific Azure tenant

* [ ] Outstanding issues
	* [ ] Limit standard users to only see and modify their own data


##	Project Status:
- [ ] Planning
- [ ] Prototype
- [X] In Development
- [ ] In Production
- [ ] Unsupported
- [ ] Retired


##	Authors and Acknowledgement
README based on <https://www.makeareadme.com/>

