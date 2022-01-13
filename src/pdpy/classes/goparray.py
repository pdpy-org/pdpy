#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Class Definitions for GOP Array """

from .base import Base
from .default import GOPArrayFlags
from ..util.utils import  log

__all__ = [ 'PdGOPArray' ]

class PdGOPArray(Base):
  """ A Pd Type
  
  Description
  -----------
  A PdGOPArray instance extends the Base class with an `addflag` method
  to account for GOPArrayFlags. And, a `__pd__` method to return a
  string representation of the PdGOPArray.

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
    print("Pdtype", self.__type__, self.__cls__)

  def addflag(self, flag):
    # log(1, "Adding flag: {}".format(flag))
    if flag is not None and flag.isnumeric():
      self.flag = GOPArrayFlags[int(flag)]
    elif flag in GOPArrayFlags:
      self.flag = flag
    else:
      self.flag = None

  def __pd__(self):
    """ Return a string representation of the PdGOPArray """
    
    if hasattr(self, 'template'):
      return f"array {self.name} {self.template}"
    
    elif self.__cls__ in ('array','obj'):
      s = super().__pd__(f"{self.name} {self.length} {self.type} {self.flag}")
      for x in getattr(self, 'data', []):
        s += x.__pd__()
      return s
    
    else:
      log(1, "Unknown PdGOPArray format: {}".format(self.__cls__))
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
