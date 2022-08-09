#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Class Definitions for GOP Array """

from .base import Base
from .data import Data
from .default import GOPArrayFlags
from ..util.utils import  log

__all__ = [ 'GOPArray' ]

class GOPArray(Base):
  """ A Pd Type
  
  Description
  -----------
  A GOPArray instance extends the Base class with an `addflag` method
  to account for GOPArrayFlags. And, a `__pd__` method to return a
  string representation of the GOPArray.

  Parameters
  ----------
  json : dict
    A dictionary of the JSON object. For example: 
    ```
    {
      'name' : 'array_name',
      'length' : 100,
      'type' : 'float',
      'flag' : 0,
      'className' : 'goparray'
    }
    ```

  """
  def __init__(self, json=None, **kwargs):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(**kwargs)
    if json is not None:
      super().__populate__(self, json)
    if hasattr(self, 'className') and self.className == 'goparray':
      self.__cls__ = 'array'
    else:
      self.__cls__ = 'array'
      self.name = 'array1'
      self.length = self.__d__.array['size']
      self.type = self.__d__.array['type']
      self.flag = self.__d__.array['flag']
      if 'data' in kwargs:
        _data = kwargs.pop('data')
      else:
        _data = [0 for _ in range(1 + self.length)]
      if 'head' in kwargs:
        _head = kwargs.pop('head')
      else:
        _head = 0
      super().__setdata__(self, Data(data=_data, head=_head))

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
