#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Base Class """

import json
from ..util.utils import log

__all__ = [ "Base" ]

def filter_underscores(o):
  return { 
    k : v 
    for k,v in o.__dict__.items() 
    if not k.startswith("__") or k=="__pdpy__"
  }

class Base(object):
  def __init__(self):
    self.patchname = None
    return self
  
  def __setattr__(self, name, value):
    if value is not None:
        self.__dict__[name] = value

  def toJSON(self):
    return json.dumps(self,
      default=filter_underscores,
      sort_keys=False,
      indent=4)
  
  def dumps(self):
    print(self.toJSON())

  def num(self, n):
    pdnm = None
    if isinstance(n, str):
      if "#" in n: pdnm = n # skip css-style colors preceded by '#'
      elif ("e" in n or "E" in n) and ("-" in n or "+" in n):
        pdnm = "{:e}".format(int(float(n)))
      elif "." in n: pdnm = float(n)
      else:
        pdnm = int(n)
    elif isinstance(n, list):
      # print("num(): input was a list of str numbers", n)
      pdnm = list(map(lambda x:self.num(x),n))
    else:
      pdnm = n
    return pdnm

  def pdbool(self, n):
    if n == "True":
      return True
    elif n == "False":
      return False
    else:
      return bool(int(float(n)))

  def __populate__(self, scope, json_dict):
    if not hasattr(json_dict, 'items'):
      log(1, "json_dict is not a dict")
      if not hasattr(json_dict, '__dict__'):
        raise Exception("json_dict is not a dict or a class")
      json_dict = json_dict.__dict__
    else:
      map(lambda k,v: setattr(scope, k, v), json_dict.items())

