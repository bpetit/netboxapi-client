#!/usr/bin/python

import argparse
import requests
import logging
import json
import sys
import os
from urlparse import urlparse, parse_qsl
from urllib import urlencode


class Api(object):
    """Api.

    Permits to send http rest requests, to the api endpoint.
    Paths in the url have to be initialized by another peace
    of code before using this class functions.
    """

    def __init__(self, *args, **kwargs):
        """__init__

        Initializes __url __headers and __token variables,
        which are used to build requests to the api.

        :param *args:
        :param **kwargs: should contain at least 'url' and 'token'
        """
        logging.basicConfig(filename='netboxapi.log', level=logging.DEBUG)
        self.__url = kwargs.get('url')
        self.__last_reply = None
        self.__headers = {}
        self.__token = None
        if 'token' in kwargs:
            self.__token = kwargs.get('token')
            self.__headers['Authorization'] = "Token {}".format(self.__token)
            self.__headers['Accept'] = "application/json; indent=4"
            self.__headers['Content-Type'] = "application/json"
        logging.info("Header: {}".format(self.__headers))

    def __log_last_request_and_reply(self):
        """__log_last_request_and_reply

        Records __last_reply content via logging module.
        (should appear in the log file though)
        """
        logging.info(
            "POST Status code: {0} Reason: {1} Request: {2} {3}\n \
            Response: {4}".format(
            self.__last_reply.status_code,
            self.__last_reply.reason,
            self.__last_reply.request.headers,
            self.__last_reply.request.body,
            self.__last_reply.text.encode('utf-8')
            )
        )

    def get(self, path="", params=""):
        """get

        Triggers a get http request to the http api endpoint. Returns the
        result as a Response object.

        :param path: The path to provide after https://{self.__url}/api/
        :param params: '?param1=foo&param2=bar' stuff, as a string.
        """
        try:
            if len(params) > 0:
                path = "{}/{}".format(path, params)
            self.__last_reply = requests.get(
                "{0}/api/{1}".format(self.__url, path),
                headers=self.__headers, verify=False
            )
            self.__log_last_request_and_reply()
        except requests.exceptions.SSLError:
            logging.warning("Certificate verify failed.")
        return self.__last_reply

    def get_id_by_name(self, path="", name=""):
        """get_id_by_name

        Returns the numerical id of an object based on its name.

        :param path: The path to provide after https://{self.__url}/api/
        :param name: The name of the object.
        """
        # Support pagination
        page = 0
        params="format=json"
        next = True
        while next:
            page += 1
            self.get(path, "?{}".format(params))
            try:
                elements = self.__last_reply.json()
                for e in elements['results']:
                    if 'name' in e:
                        if e['name'] == name:
                            return e['id']
                    else:
                        if e['model'] == name:
                            return e['id']

                # Support pagination
                if elements['next'] is None:
                    next = False
                else:
                    params = urlparse(elements['next']).query

            except ValueError:
                print('Malformed JSON on {}/?{}, Skipping ...'.format(path, params))
                qs = dict(parse_qsl(params))
                qs['offset'] = unicode(str(int(qs['offset']) + int(qs['limit'])))
                params = urlencode(qs)
        return None

    def list(self, path=""):
        """list

        Returns the complete list of concerned objects.

        :param path: The path to provide after https://{self.__url}/api/
        """
        self.get(path, params="?limit=0")
        return self.__last_reply

    def post(self, path="", payload={}):
        """post

        Pushes content of payload as a post request.

        :param path: The path to provide after https://{self.__url}/api/
        :param payload: The content of the post request.
        """
        try:
            self.__last_reply = requests.post(
                "{0}/api/{1}".format(self.__url, path), headers=self.__headers,
                data=json.dumps(payload), verify=False
            )
            self.__log_last_request_and_reply()
            return self.__last_reply
        except requests.exceptions.SSLError:
            logging.warning("Certificate verify failed.")

    def delete(self, path=""):
        """delete

        Sends an http rest delete request.

        :param path: The path to provide after https://{self.__url}/api/
        """
        try:
            self.__last_reply = requests.delete(
                "{0}/api/{1}".format(self.__url, path),
                headers=self.__headers, verify=False
            )
            self.__log_last_request_and_reply()
            return self.__last_reply
        except requests.exceptions.SSLError:
            logging.warning("Certificate verify failed.")
        except ValueError:
            logging.warning("ValueError")

    def put(self, path="", payload={}):
        """put

        Sends an http rest put request.

        :param path: The path to provide after https://{self.__url}/api/
        :param payload: The payload of the put request.
        """
        try:
            self.__last_reply = requests.put(
                "{0}/api/{1}/".format(self.__url, path),
                headers=self.__headers, data=json.dumps(payload),
                verify=False
            )
            self.__log_last_request_and_reply()
            return self.__last_reply
        except requests.exceptions.SSLError:
            logging.warning("Certificate verify failed.")

    def patch(self, path="", payload={}):
        """patch

        :param path:
        :param payload:
        """
        try:
            self.__last_reply = requests.patch(
				"{0}/api/{1}/".format(self.__url, path),
				headers=self.__headers, data=json.dumps(payload),
				verify=False
			)
            return self.__last_reply
        except requests.exceptions.SSLError:
            logging.warning("Certificate verify failed.")


# == Main CLI
#
# === Helpers
#
def print_json(obj):
    print( json.dumps(
        obj,
        sort_keys=True,
        indent=4, separators=(',', ': ')
    ))


# === Commands
#
def show(api, model, obj, ident=None, name=None):
    """show

    Calls api object and its get function (and optionally get_id_by_name).
    Displays and returns response as json data.

    :param api: Api object
    :param model: string, tells which data model to use
    :param obj: string, tells which object to use
    :param ident: int, numerical identifier of the object
    :param name: string, name of the object
    """
    res = get(api, model, obj, ident, name)

    # Display
    print_json(res)
    return res

def get(api, model, obj, ident=None, name=None):
    """get

    Calls api object and its get function (and optionally get_id_by_name).
    Returns response as json data.

    :param api: Api object
    :param model: string, tells which data model to use
    :param obj: string, tells which object to use
    :param ident: int, numerical identifier of the object
    :param name: string, name of the object
    """
    if ident is None and name is not None:
        ident = api.get_id_by_name(
            "{}/{}".format(model, obj), name
        )
    return api.get(
            "{}/{}/{}".format(
                model, obj, ident
            )
        ).json()

def enum(api, model, obj, **kwargs):
    """enum

    Displays and returns all instances of an object, as json data.

    :param api: Api object
    :param model: string, tells which data model to use
    :param obj: string tells which object to use
    :param **kwargs:
    """
    res = get_list(api, model, obj)
    print_json(res)
    return res

def get_list(api, model, obj, **kwargs):
    """get_list

    Returns all instances of an object, as json data.

    :param api: Api object
    :param model: string, tells which data model to use
    :param obj: string tells which object to use
    :param **kwargs:
    """
    if model and obj:
        res  = api.get("{}/{}/".format(model, obj)).json()
        return res

def get_list_grouped_by_tenant(api, model, obj, **kwargs):
    """get_list_grouped_by_tenant

    :param api: Api object
    :param model: string, tells which data model to use
    :param obj: string tells which object to use
    :param **kwargs:
    """
    res = get_list(api, model, obj)
    by_tenants = {}
    for dev in res['results']:
        if 'tenant' in dev and dev['tenant']:
            if dev['tenant']['name'] not in by_tenants.keys():
                by_tenants[dev['tenant']['name']] = {}
                by_tenants[dev['tenant']['name']]['hosts'] = []
            by_tenants[dev['tenant']['name']]['hosts'].append(dev['name'])
        else:
            if 'unclassified' not in by_tenants.keys():
                by_tenants['unclassified'] = { 'hosts': [] }
            by_tenants['unclassified']['hosts'].append(dev['name'])
    return by_tenants

def create(api, model, obj, data, ident=None, name=None):
    """create

	Creates an object.

    :param api: Api object
    :param model: string, tells which data model to use
    :param obj: string tells which object to use
    :param data: dict, containing data for the object we create
    :param ident: int, numerical identifier of the object
    :param name: string, name of the object
    """
    res = None
    if model and obj and data:
        res = api.post(
            path="{}/{}/".format(model, obj),
            payload=data
        ).json()
    return res

def delete(api, model, obj, ident=None, name=None):
    """delete

    Calls api object delete function in order to delete an object.
    The selection is based on id or name of the object.

    :param api: Api object
    :param model: string, tells which data model to use
    :param obj: string tells which object to use
    :param ident: int, numerical identifier of the object
    :param name: string, name of the object
    """
    if (ident is None) and name is not None:
        ident = api.get_id_by_name("{}/{}".format(
            model, obj), name
        )
    res = api.delete(
        path="{}/{}/{}".format(model, obj, ident)
    )
    # Response.json() raises an exception when there is no data,
    # and it seems normal: https://github.com/requests/requests/issues/4186
    result = None
    try:
        result = res.json()
    except ValueError:
        result = res.text
    return result


def update(api, model, obj, data, ident=None, name=None, **kwargs):
    """update

    Calls api object put function in order to edit the object.
    Object can be selected by id or by name.

    TODO: raise exception if required fields are not provided

    :param api: Api object
    :param model: string, tells which data model to use
    :param obj: string tells which object to use
    :param data: dict, containing data for the object we update
    :param ident: int, numerical identifier of the object
    :param name: string, name of the object
    :param **kwargs:
    """
    if (ident is None) and name is not None:
        ident = api.get_id_by_name("{}/{}".format(
            model, obj), name
        )
    path = "{}/{}/{}".format(model, obj, ident)
    res = api.put(
        path=path,
        payload=data
    )
    try:
        result = res.json()
    except ValueError:
        result = res.text
    return result

def patch(api, model, obj, data, ident=None, name=None, **kwargs):
    """patch

    Calls api object patch function in order to edit some fields of the object.
    The difference with update is that this function calls the patch method of
	the API, allowing to edit fields of the object without overriding all the fields.

    :param api: Api object
    :param model: string, tells which data model to use
    :param obj: string, tells which object to use
    :param data: dict, containing data for the object we update
    :param ident: int, numerical identifier of the object
    :param name: string, name of the object
    :param **kwargs:
    """
    if (ident is None) and name is not None:
        ident = api.get_id_by_name("{}/{}".format(
            model, obj), name
        )
    path = "{}/{}/{}".format(model, obj, ident)
    res = api.patch(
        path=path,
        payload=data
    )
    try:
        result = res.json()
    except ValueError:
        result = res.text
    return result
