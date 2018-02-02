#!/usr/bin/python

import argparse
import json
import os, sys
from netboxapi_client import Api, create, show, enum, delete, update, patch
import urllib3

def get_configuration(path="{}/netboxapi.json".format(os.getcwd())):
    """get_configuration

    Returns a dictionnary containing all elements written as json, in the
    configuration file.

    :param path:
    """
    try:
        with open(path) as fd:
            return json.load(fd)
    except Exception:
        print("No configuration file found at {}. Reading environment variables NETBOXAPI_TOKEN and NETBOXAPI_URL.".format(path))
        if 'NETBOXAPI_TOKEN' in os.environ and 'NETBOXAPI_URL' in os.environ:
          config = { "url": os.environ.get('NETBOXAPI_URL'), "token": os.environ.get('NETBOXAPI_TOKEN') }
          return config
        else:
          print("Configuration not properly defined.")
        sys.exit(254)

def main():
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

    # Disable InsecureRequestWarning
    if 'insecure' in config:
        if 'True' in config['insecure']:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
        'patch': patch
    }

    DESCRIPTION_MAP = {
        'show': "Shows an object's data.",
        'list': "Lists objects.",
        'create': "Creates object.",
        'delete': "Deletes object",
        'update': "Updates object. It is required to fill all fields you want to be filled for that object.",
        'patch': "Updates one or some fields of an object. Unlike update method, you can specify only the fiels you want to update."
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
        },
        'configuration_file': {
          'option': '-c',
          'type': str,
          'help': "Path to the json configuration file.",
          'dest': 'config'
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
                    k, help="{}".format(DESCRIPTION_MAP[k])
                )
                for k, arg in ARGUMENTS.items():
                    action_parser.add_argument(
                        arg['option'],
                        type=arg['type'],
                        help=arg['help'],
                        dest=arg['dest'],
                    )
    ns = parser.parse_args()
    if 'action' in ns:
        if 'data' in ns and ns.data:
                pprint(
                    FUNCTION_MAP[ns.action](
                        api=api,
                        model=ns.model,
                        obj=ns.object,
                        ident=ns.id,
                        name=ns.name,
                        data=json.loads(ns.data)
                    )
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
