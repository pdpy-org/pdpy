#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" test class """
import pdpy_lib as pdpy
import json
# from types import SimpleNamespace

from pdpy_lib 
import PdPy

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
    return getattr(pdpy, pdpyName)(json=obj)
  return obj

file="/Users/fd/Development/pdpy/src/tests/json_files/all_objects.pd.json"

with open(file, "r", encoding='utf-8') as fp:
  data = json.load(fp, object_hook=PdPyEncoder)
  data = PdPy(json=data)

with open('test.json','w') as fp:
  fp.write(data.__json__())
