# netboxapi-client
Small python client for netbox (https://github.com/digitalocean/netbox) API

## CLI usage

### Using a config file

Copy `netboxapi.json.example` file to `netboxapi.json` and edit that file to match your netbox instance url and token.

`python netboxapi_client.py -h` will give you the overview of the models you can act on. `-h` is available at each depth level of the cli.

## TODO

- prevent sending multiple requests/discovering the model if not required
- better catch exceptions to give users a more comprehensive output
