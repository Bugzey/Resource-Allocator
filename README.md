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
(TBA)

Within a particular ecosystem, there may be a common way of installing things, such as using Yarn,
NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a
novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people
to using your project as quickly as possible. If it only runs in a specific context like a
particular programming language version or operating system or has dependencies that have to be
installed manually, also add a Requirements subsection. 


##	Usage
(TBA)

Use examples liberally, and show the expected output if you can. It's helpful to have inline the
smallest example of usage that you can demonstrate, while providing links to more sophisticated
examples if they are too long to reasonably include in the README. 


##	Contributing
Features and bug fixes should be written in their own separate git branches stemming from the head
of the master branch. Automated testing using the `unittest` framework is strongly encouraged.

Outstanding features and associated tasks will be tallied in this README file until further notice.

Feature brainstorm:

* [ ] database objects
	* [X] user
	* [X] resource
	* [X] resource group (can be recursive)
	* [X] iteration - type of time iteration to request resources for (?)
	* [X] request - pending user requests
	* [ ] resource to resource group - many-to-many mapping
	* [ ] allocation - resource X user X iteration X exact date

* [ ] endpoints:
	* [ ] /users/ - list all users (admin required)
	* [X] /resource/ - list all resources
	* [X] /resource_group/ - (?)
	* [X] /iteration/ - create, list
	* [X] /request/ - post a request for a resource
	* [ ] /resource_to_resource_group/ - many-to-many mapping
	* [ ] /allocation( - start the automatic allocation, be able to pass overrides

* [ ] allocation algorithm - initial + partial addition?
	* [ ] apply overrides without question
	* [ ] distribute weights according to request preferences - each user has 10 points
	* [ ] assign an additional 2 points to history - if the person is assigned to the previous
	  last resource they used or were assigned to
	* [ ] Use simplex algorithm? Alternatively try to sort days by possible preference points
	  (getting combinatorical here)

* [ ] Third-party integration
	* [ ] Optional log-in via Azure Active Directory (AD) for a specific Azure tenant


##	Project Status:
- [ ] Planning
- [ ] Prototype
- [X] In Development
- [ ] In Production
- [ ] Unsupported
- [ ] Retired


##	Authors and Acknowledgement
README based on <https://www.makeareadme.com/>

