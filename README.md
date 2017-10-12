# netboxapi-client

This is a python client for netbox (https://github.com/digitalocean/netbox) API. It can be used either as a python module/library or directly from the command line.
The goal of this project is to provide a simple way to automate infrastructure documentation based on the REST API from that great project that is Netbox.

## Status

Under development

## Installation

You can clone that repo and install locally with:

	python setup.py build && pip install -e .

Proper pypi package on it's way.

## Usage

### From CLI, using a configuration file

Copy `netboxapi.json.example` file to `netboxapi.json` and edit that file to match your netbox instance url and token.

`python netboxapi_client.py -h` will give you the overview of the models you can act on. `-h` is available at each depth level of the cli.

### From code

This is a very basic example:

	from pprint import pprint
	from netboxapi_client import Api, get

	TOKEN = "thetokenyoucangetfromnetboxwebuionauserprofilepage"
	URL = "https://netbox.example.org"

	api = Api(url=URL, token=TOKEN)

	res = get(api, model="dcim", obj="devices", name="sw-02-par-eq2")

	pprint(res)

For now, you have to import the Api class and the function you need (get, get_list, update, create, delete, and so on...). This will be improved soon...

## TODO

- prevent sending multiple requests/discovering the model if not required
- better catch exceptions to give users a more comprehensive output
