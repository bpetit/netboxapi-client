#!/usr/bin/python

import unittest
from netboxapi_client import Api, enum, get_list, create, delete, get
from pprint import pprint

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
        res = enum(self.__api, model="ipam", obj="aggregates")
        self.assertTrue(type(res['results']) is list)
        self.assertGreaterEqual(len(res['results']), 1)

    def test_enum_no_objects(self):
        """
        """
        res = enum(self.__api, model="dcim", obj="devices")
        self.assertTrue(type(res['results']) is list)
        self.assertEqual(len(res['results']), 0)

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

if __name__ == '__main__':
    unittest.main()
