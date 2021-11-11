#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" test class """
import pdpy
import json
# from types import SimpleNamespace

from pdpy.classes.pdpy import PdPy

# with open('tests/import_dict.json','r') as f:
#   d = json.load(f)

def PdPyEncoder(obj):
  if '__pdpy__' in obj:
    pdpyName = obj['__pdpy__']
    # print(pdpyName, obj)
    # obj = set(map(lambda x:PdPyEncoder(x),obj))
    # this line grabs the class from the module
    # and creates an instance of it
    # passing the json object as the argument
    return getattr(pdpy, pdpyName)(json_dict=obj)
  return obj

file="/Users/fd/Development/pdpy/src/tests/json_files/all_objects.pd.json"

with open(file, "r", encoding='utf-8') as fp:
  data = json.load(fp, object_hook=PdPyEncoder)
  data = PdPy(json_dict=data)

with open('test.json','w') as fp:
  fp.write(data.toJSON())
