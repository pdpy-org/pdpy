#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" 
GOP Array
=========
"""

from . import data
from ..core.base import Base
from ..utilities.default import GOPArrayFlags
from ..utilities.utils import log

__all__ = [ 'GOPArray' ]

class GOPArray(Base):
  """ A Graph-on-Parent Array representation
  
  A GOPArray instance extends the Base class with an `addflag` method
  to account for GOPArrayFlags. And, a `__pd__` method to return a
  string representation of the GOPArray.

  Parameters
  ----------
  json : dict
    A dictionary of the JSON object. For example: ```{ 'name' : 'array_name', 'length' : 100, 'type' : 'float', 'flag' : 0, 'className' : 'goparray'}```
  
  **kwargs:
    Other keyword arguments such as ``name``, ``head``, ``length``, and ``data``

  """
  def __init__(self, json=None, **kwargs):
    self.__pdpy__ = self.__class__.__name__
    
    super().__init__()

    if json is not None:
      super().__populate__(self, json)

    if hasattr(self, 'className') and self.className == 'goparray':
      self.__cls__ = 'array'
    else:
      self.__cls__ = 'array'
      
    if 'name' in kwargs:
      self.name = kwargs.pop('name')
    
    if 'head' in kwargs:
      _head = kwargs.pop('head')
    else:
      _head = 0
    
    if 'length' in kwargs:
      self.length = kwargs.pop('length')
    else:
      self.length = self.__d__.array['size']
    
    if 'data' in kwargs:
      _data = kwargs.pop('data')
    else:
      _data = [0 for _ in range(1 + self.length)]
    
    
    self.type = self.__d__.array['type']
    self.flag = self.__d__.array['flag']
    
    super().__setdata__(self, data.Data(data=_data, head=_head))

    # print("Pdtype", self.__type__, self.__cls__)

  def addflag(self, flag):
    # log(1, "Adding flag: {}".format(flag))
    if flag is not None and flag.isnumeric():
      self.flag = GOPArrayFlags[int(flag)]
    elif flag in GOPArrayFlags:
      self.flag = flag
    else:
      self.flag = None

  def __pd__(self):
    """ Return a string representation of the GOPArray """
    
    if hasattr(self, 'template'):
      return "array " + str(self.name) + " " + str(self.template)
    
    elif self.__cls__ in ('array', 'obj'):
      s = super().__pd__(" ".join(map(lambda x:str(x),[self.name,self.length,self.type,self.flag])))
      for x in getattr(self, 'data', []):
        s += x.__pd__()
      return s
    
    else:
      log(1, "Unknown GOPArray format: {}".format(self.__cls__))
      self.__dumps__()
      return 
  
  def __xml__(self):
    """ Return the XML Element for this object """
    x = super().__xml__(scope=self, attrib=('name', 'template', 'length', 'type', 'flag', 'className'))
    if hasattr(self, 'data'):
      data = super().__element__(tag='data')
      for d in self.data:
        super().__subelement__(data, d.__xml__())
      super().__subelement__(x, data)
    return x
