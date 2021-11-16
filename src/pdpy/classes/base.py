#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Base Class """

import json
from ..util.utils import log, splitByEscapedChar

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

  def __fill__(self, data, dtype=float, char=None):
    if char is not None:
      setattr(self, 'data', splitByEscapedChar(data, char=char))
    else:
      setattr(self, 'data', [dtype(d) for d in data])

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

    if hasattr(scope, 'className') and self.__cls__ is None:
      self.__cls__ = scope.className 

  def __pd__(self, args=None):
    """ Returns a the pd line for this object
    
    Description
    -----------
    
    Parameters
    -----------
    args : `list` of `str` or `str` or `None`
      The arguments to the pd line.
    
    If args is present, the pd line will end with `;\r\n` with the arguments:
      If args is a list of strings, each element is appended to the pd line.
        `#N canvas 0 22 340 520 12;`
      If args is a string, it is appended to the pd line: 
        `#X obj 10 30 print;`
    If args is None, the pd line is returned without arguments: 
      `#X connect`

    Returns
    -----------
    `str` : the pd line for this object built with `__type__` and `__cls__`

    """
    
    s = f'#{self.__type__} {self.__cls__}'

    if args is None:
      return s
    else:
      if isinstance(args, list):
        s += ' ' + ' '.join(args)
      else:
        s += f' {args}'
      return s + self.__end__

