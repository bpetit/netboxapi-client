#!/usr/bin/python3

import argparse
import requests
import logging
import json
import sys
import os
from pprint import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning


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
            self.__last_reply.text
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
        self.get(path, "?limit=0")
        elements = self.__last_reply.json()
        for e in elements['results']:
            if e['name'] == name:
                return e['id']
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
                "{0}/api/{1}".format(self.__url, path),
                headers=self.__headers, data=json.dumps(payload),
                verify=False
            )
            self.__log_last_request_and_reply()
            return self.__last_reply
        except requests.exceptions.SSLError:
            logging.warning("Certificate verify failed.")


def show(api=None, **kwargs):
    """show

    Calls api object and its get function (and optionally get_id_by_name).
    Displays response as json data.
    """
    if 'ident' in kwargs and kwargs['ident'] is not None:
        ident = kwargs['ident']
    elif "name" in kwargs:
        ident = api.get_id_by_name(
            "{}/{}".format(kwargs['model'], kwargs['obj']), kwargs['name']
        )
    pprint(
        api.get(
            "{}/{}/{}".format(
                kwargs['model'], kwargs['obj'], ident
            )
        ).json()
    )

def get(api=None, **kwargs):
    """show

    Calls api object and its get function (and optionally get_id_by_name).
    Displays response as json data.
    """
    if 'ident' in kwargs and kwargs['ident'] is not None:
        ident = kwargs['ident']
    elif 'name' in kwargs:
        ident = api.get_id_by_name(
            "{}/{}".format(kwargs['model'], kwargs['obj']), kwargs['name']
        )
    return api.get(
            "{}/{}/{}".format(
                kwargs['model'], kwargs['obj'], ident
            )
        ).json()

def enum(api=None, model=None, obj=None, **kwargs):
    """enum

    Displays all instances of an object, as json data.

    :param **kwargs:
    """
    if model and obj:
        res = api.get("{}/{}/".format(model, obj)).json()
        pprint(res)
        return res


def create(api=None, **kwargs):
    """create

    Calls api object post function in order to create a new object.
    Returns response as json data.

    :param **kwargs:
    """
    res = None
    if 'model' and 'obj' and 'data' in kwargs:
        res = api.post(
            path="{}/{}/".format(kwargs['model'], kwargs['obj']),
            payload=kwargs['data']
        ).json()
        pprint(res)
    return res



def delete(api=None, **kwargs):
    """delete

    Calls api object delete function in order to delete an object.
    The selection is based on id or name of the object.

    :param **kwargs:
    """
    pprint(kwargs)
    if (not 'ident' in kwargs or kwargs['ident'] is None) and 'name' in kwargs:
        ident = api.get_id_by_name("{}/{}".format(
            kwargs['model'], kwargs['obj']), kwargs['name']
        )
    res = api.delete(
        path="{}/{}/{}".format(kwargs['model'], kwargs['obj'], ident)
    )
    try:
        # Response.json() raises an exception when there is no data,
        #and it seems normal: https://github.com/requests/requests/issues/4186
        pprint(res.json())
    except ValueError:
        pprint(res)


def update(api=None, **kwargs):
    """update

    Calls api object put function in order to edit some elements of an object.
    Object can be selected by id or by name.

    :param **kwargs:
    """
    if 'ident' in kwargs:
        ident = kwargs['ident']
    else:
        ident = None
    if (not 'ident' in kwargs or kwargs['ident'] is None) and 'name' in kwargs:
        ident = api.get_id_by_name("{}/{}".format(
            kwargs['model'], kwargs['obj']), kwargs['name']
        )
    path = "{}/{}/{}".format(kwargs['model'], kwargs['obj'], ident)
    pprint(kwargs['data'])
    res = api.put(
        path=path,
        payload=kwargs['data']
    )
    pprint(res.json())


def get_configuration(path='netboxapi.json'):
    """get_configuration

    Returns a dictionnary containing all elements written as json, in the
    configuration file.

    :param path:
    """
    try:
        with open(path) as fd:
            return json.load(fd)
    except OSError as fne:
        print("No configuration file found at {}.".format(path))
        pprint(fne)
        sys.exit(254)


def main():
    #TODO: ensure this is not necessary anymore on Ubuntu > 16.04
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    parser = argparse.ArgumentParser()

    ## NOT IMPLEMENTED YET
    #parser.add_argument(
    #    "--url",
    #    help="URL of the target Netbox instance",
    #    dest='url'
    #)
    #parser.add_argument(
    #    "--token",
    #    help="Token that should be used for authentication",
    #    dest='token'
    #)

    config = get_configuration()
    pprint(config)
    api = Api(
        url=config['url'],
        token=config['token']
    )

    subparsers = parser.add_subparsers(dest='model')

    mydict = api.get('').json()

    FUNCTION_MAP = {
        'show': show,
        'list': enum,
        'create': create,
        'delete': delete,
        'update': update,
    }

    ARGUMENTS = {
        'identifier': {
            'option': '-i',
            'type': int,
            'help': "Numerical id of the object",
            'dest': 'id'
        },
        'data_file': {
            'option': '-d',
            'type': str,
            'help': "Path to the file containing json data.",
            'dest': 'data'
        },
        'name': {
            'option': '-n',
            'type': str,
            'help': "Name of the object.",
            'dest': 'name'
        }
    }

    for model in mydict.keys():
        model_parser = subparsers.add_parser(
            model,
            help="{0} objects".format(model)
        )
        model_subparser = model_parser.add_subparsers(dest='object')
        for elmt in api.get(model+'/').json():
            elmt_parser = model_subparser.add_parser(
                elmt,
                help="manage {0}".format(elmt)
            )
            action_subparser = elmt_parser.add_subparsers(dest="action")
            for k, v in FUNCTION_MAP.items():
                action_parser = action_subparser.add_parser(
                    k, help="{}".format(k)
                )
                for k, arg in ARGUMENTS.items():
                    action_parser.add_argument(
                        arg['option'],
                        type=arg['type'],
                        help=arg['help'],
                        dest=arg['dest'],
                    )
    ns = parser.parse_args()
    pprint(ns)
    if 'action' in ns:
        if 'data' in ns and ns.data:
                FUNCTION_MAP[ns.action](
                    api=api,
                    model=ns.model,
                    obj=ns.object,
                    ident=ns.id,
                    name=ns.name,
                    data=json.loads(ns.data)
                )
        else:
            FUNCTION_MAP[ns.action](
                api=api,
                model=ns.model,
                obj=ns.object,
                ident=ns.id,
                name=ns.name
            )

if __name__ == "__main__":
    main()
