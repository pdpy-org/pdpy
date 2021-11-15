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
  def __init__(self, patchname=None, pdtype=None, cls=None):
    self.patchname = patchname # the name of the patch
    self.__end__ = ';\r\n' # The pd line end character sequence
    self.__type__ = pdtype if pdtype is not None else 'X' # one of X, N, or A
    self.__cls__ = cls # one of obj, msg, text, etc.

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
    if n == "True" or n == "true":
      return True
    elif n == "False" or n == "false":
      return False
    else:
      return bool(int(float(n)))

  def __populate__(self, scope, json_dict):
    # TODO: protect against overblowing scope
    if not hasattr(json_dict, 'items'):
      log(1, scope.__class__.__name__, "json_dict is not a dict")
      if not hasattr(json_dict, '__dict__'):
        raise log(2, scope.__class__.__name__, "json_dict is not a class")
      json_dict = json_dict.__dict__
    
    # map(lambda k,v: setattr(scope, k, v), json_dict.items())
    for k,v in json_dict.items():
      setattr(scope, k, v)

  def __pd__(self, args=None):
    s = f"#{self.__type__} {self.__cls__}"
    if args is not None:
      if isinstance(args, list):
        s += ' ' + ' '.join(args)
      else:
        s += f" {args}"
    return s + self.__end__

