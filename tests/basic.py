#!/usr/bin/python

import unittest
from netboxapi_client import Api, enum, get_list
from pprint import pprint

TOKEN = "2b2b00559b133a499c027e6a60efd7b0e87a6876"
URL = "http://localhost:8000"

class BasicTest(unittest.TestCase):
  """
  """

  __api = Api(
    url=URL,
    token=TOKEN
  )

  __models = ['circuits', 'dcim', 'ipam', 'extras', 'tenancy']

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

if __name__ == '__main__':
  unittest.main()
