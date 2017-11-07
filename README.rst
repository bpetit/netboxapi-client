netboxapi-client
================

This is a python client for netbox (https://github.com/digitalocean/netbox) API. It can be used either as a python module/library or directly from the command line.
The goal of this project is to provide a simple way to automate infrastructure documentation based on the REST API from that great project that is Netbox.

Status
------

Under development.

Current developments are tested on netbox v2.2.2 and above.

Installation
------------

From pypi:

.. code-block:: bash

  pip install netboxapi-client #until the pre-release flag is removed you may have to force installation asking specifically for a release ie: pip install netboxapi-client==0.1b1

If you want to test the latest develoment version, you can clone that repo and install locally with:

.. code-block:: bash

	python setup.py build && pip install -e .

Usage
-----

You need a small configuration file to run the client. That file has, for now, to be named **netboxapi.json** and has to be in the current directory. It should be of that form:

.. code-block:: json

  {
    "url": "https://netbox.example.org",
    "token": "thisisatokenyoucangetfromthewebinterfacesettingspage"
  }

`python netboxapi_client.py -h` will give you the overview of the models you can act on. `-h` is available at each depth level of the cli.

Here are some examples:

.. code-block:: bash

	netboxapi_client -h
	netboxapi_client dcim -h category
	netboxapi_client dcim devices -h
	netboxapi_client dcim devices list
	netboxapi_client dcim devices create -d '$(cat mydevice.json)'
	netboxapi_client dcim devices create \
		-d '{ "name": "sw-02-par-eq2", \
		      "slug": "sw-02-par-eq2", \
		      "device_role": "1", \
		      "device_type": "8", \
		      "site": "184" }'
	netboxapi_client dcim devices show -n sw-02-par-eq2
	netboxapi_client dcim devices show -i 10
	netboxapi_client dcim devices delete -n sw-02-par-eq2

From code:

This is a very basic example:

.. code-block:: python

	from pprint import pprint
	from netboxapi_client import Api, get

	TOKEN = "thetokenyoucangetfromnetboxwebuionauserprofilepage"
	URL = "https://netbox.example.org"

	api = Api(url=URL, token=TOKEN)

	res = get(api, model="dcim", obj="devices", name="sw-02-par-eq2")

	pprint(res)

For now, you have to import the Api class and the function you need (get, get_list, update, create, delete, and so on...). This will be improved soon...

How-to test
-----------

Install docker and docker-compose and then:

.. code-block:: bash

  sudo docker-compose run --rm netbox createsuperuser

You will be prompted for a username, email and password for the superuser.

.. code-block:: bash

  sudo docker-compose up -d

Then you have to connect to the netbox instance you just installed. It should be accessible at http://localhost:8000 . Login with the credentials you choosed earlier. On the top right you can select username > profile. Then click on "API tokens" and create one, either use the one writen in tests/basic.py or choose one and replace the one in this file. (yeah token creation could be automated, it will be...)

Then you can try querying the api as described earlier.

To run unit tests:

.. code-block:: bash

  python tests/basic.py

TODO
----

- prevent sending multiple requests/discovering the model if not required
- better catch exceptions to give users a more comprehensive output
- setup CI/CD pipeline and build status on github
- push docker image to public repo and add docker-compose.yml, entrypoint.sh to the repo, add testing process to documentation
