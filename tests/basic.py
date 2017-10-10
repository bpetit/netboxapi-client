#!/usr/bin/python

import unittest
from netboxapi_client import Api, get_list, create, delete, get, get_list_grouped_by_tenant

TOKEN = "2b2b00559b133a499c027e6a60efd7b0e87a6876"
URL = "http://localhost:8000"

class BasicTest(unittest.TestCase):

    def setUp(self):
        """setUp"""
        self.__api = Api(
            url=URL,
            token=TOKEN
        )
        self.__last_id = None
        self.__models = ['circuits', 'dcim', 'ipam', 'extras', 'tenancy']

    def test_enum_models(self):
        """
        Tests if the client is able to list all models.
        """
        res = self.__api.get('').json()
        for model in self.__models:
            self.assertIn(model, res.keys())

    def test_enum_object_types(self):
        """
        Tests if the client is able to list all object types from all models.
        """
        for model in self.__models:
            res = self.__api.get('{}'.format(model))
            self.assertGreaterEqual(len(res.json()), 1)

    def test_enum_objects(self):
        """
        Tests if the client is able to list all objects of a given type.
        """
        res = get_list(self.__api, model="ipam", obj="aggregates")
        self.assertTrue(type(res['results']) is list)
        self.assertGreaterEqual(len(res['results']), 1)

    def test_enum_no_objects(self):
        """
        """
        res = get_list(self.__api, model="dcim", obj="devices")
        self.assertTrue(type(res['results']) is list)

    def test_get_list_objects(self):
        """
        """
        res = get_list(self.__api, model="ipam", obj="aggregates")
        self.assertTrue(type(res['results']) is list)
        self.assertGreaterEqual(len(res['results']), 1)

    def test_delete_absent_object(self):
        res = delete(self.__api, model="dcim", obj="sites", ident=1)
        self.assertTrue(type(res) is dict)

    def test_create_object(self):
        """
        """
        res = create(
            self.__api, model="dcim", obj="sites",
            data={ 'name': 'testsite9', 'slug': 'testsite9' }
        )
        self.assertIn('id', res.keys())
        self.__last_id = res['id']

    def test_get_object(self):
        res = get(
            self.__api, model="ipam", obj="aggregates",
            ident=1
        )
        self.assertTrue(type(res) is dict)
        self.assertGreater(len(res), 1)

    def test_crud_object(self):
        res = create(
            self.__api, model="dcim", obj="sites",
            data={ 'name': 'ohvi7Xiew6VohSee1ael', 'slug': 'ohvi7Xiew6VohSee1ael' }
        )
        self.assertTrue(type(res) is dict)
        self.__last_id = res['id']
        res = get(
            self.__api, model='dcim', obj='sites',
            ident=self.__last_id
        )
        self.assertTrue(type(res) is dict)
        res = delete(
            self.__api, model="dcim", obj="sites",
            name='ohvi7Xiew6VohSee1ael'
        )
        self.assertTrue(type(res) is dict)

    def test_delete_object_by_name(self):
        res = delete(
            self.__api, model="dcim", obj="sites",
            name='testsite9'
        )
        # delete function should return a dict
        self.assertFalse(res is None)
        self.assertTrue(type(res) is dict)

    def test_get_list_by_tenant(self):
        res = create(
            self.__api, model="dcim", obj="device-roles",
            data={ 'name': 'testdev9', 'slug': 'testdev9', 'color': 'ffffff'}
        )
        device_role_id = res['id']
        res = create(
            self.__api, model="dcim", obj="sites",
            data={ 'name': 'testdev9', 'slug': 'testdev9'}
        )
        site_id = res['id']
        res = create(
            self.__api, model="dcim", obj="device-types",
            data={ 'name': 'testdev9', 'slug': 'testdev9', 'manufacturer': 1,
                'model': 'testdev9'
            }
        )
        device_type_id = res['id']
        res = create(
            self.__api, model="dcim", obj="devices",
            data={ 'name': 'testdev9', 'slug': 'testdev9', 'device_role': device_role_id, 'site': site_id, 'device_type': device_type_id }
        )
        device_id = res['id']
        res = get_list_grouped_by_tenant(
            self.__api, model="dcim", obj="devices"
        )
        self.assertTrue(type(res) is dict)
        self.assertTrue('unclassified' in res)
        self.assertTrue('hosts' in res['unclassified'])
        self.assertTrue('testdev9' in res['unclassified']['hosts'])
        res = delete(
            self.__api, model="dcim", obj="devices",
            ident=device_id
        )
        res = delete(
            self.__api, model="dcim", obj="device-roles",
            ident=device_role_id
        )
        res = delete(
            self.__api, model="dcim", obj="device-types",
            ident=device_type_id
        )
        res = delete(
            self.__api, model="dcim", obj="sites",
            ident=site_id
        )


if __name__ == '__main__':
    unittest.main()
