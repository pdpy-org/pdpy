#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Pd Types Class Definitions """

from pdpy.util.utils import log
from .base import Base
from collections import defaultdict
from itertools import zip_longest

__all__ = [
  'PdFloat',
  'PdSymbol',
  'PdList',
]

class PdFloat(Base):
  """ A PdFloat base class """
  def __init__(self, value=None, name=None, json_dict=None):
    self.__pdpy__ = self.__class__.__name__
    if json_dict is not None:
      super().__populate__(self, json_dict)
    else:
      self.value = self.num(value) if value is not None else None
      self.name = name
    
  def __pd__(self):
    return f"{self.value}"

class PdSymbol(Base):
  """ A PdSymbol base class """
  def __init__(self, value=None, name=None, json_dict=None):
    self.__pdpy__ = self.__class__.__name__
    if json_dict is not None:
      super().__populate__(self, json_dict)
    else:
      self.value = str(value) if value is not None else None
      self.name = name
  
  def __pd__(self):
    return f"{self.value}"

class PdList(Base):
  """ A PdList base class """
  def __init__(self, name=None, json_dict=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__()
    if json_dict is not None:
      super().__populate__(self, json_dict)
    else:
      self.name = name

  def addelement(self, e_type, e_key, e_value):
    """ Add a type to the list """
    
    if not hasattr(self, e_type):
      setattr(self, e_type, defaultdict(list))
    
    attr = getattr(self, e_type)
    
    attr[e_key].append(e_value)

  def __pd__(self, template):

    s = ''
    
    def __interleave__(s, attr, keys):
      """
      interleave keys variable with attr
      zip_longest takes care of filling out the list with empty strings
      if these are of different lengths
      
      logic is:
      1. for every key
      2. get the value from the attr dict
      3. return an expanded list of values
      4. zip the elements of the list together in nth number of elements
      5. filling empty values with empty strings
      """
      # log(1, 'interleave', s, attr, keys)
      for values in zip_longest(*[attr[k] for k in keys], fillvalue=''):
        # log(1, 'values:', values)
        # on every paired value
        for v in values:
          # if it is a list, iterate over it and join with a space
          if isinstance(v, list):
            for val in v:
              if isinstance(v, list):
                s += ' '.join(val)
              else:
                s += f"{val} "
            s += self.__semi__
          # otherwise, just append the value as a string
          else:
            s += ' ' + str(v)
        s += self.__semi__
      return s

    if hasattr(self, 'float') and hasattr(template, 'float'):
      keys = getattr(template, 'float')
      if keys:
        s = __interleave__(s, self.float, keys)
        s += self.__semi__
    
    if hasattr(self, 'symbol') and hasattr(template, 'symbol'):
      keys = getattr(template, 'symbol')
      if keys:
        s = __interleave__(s, self.symbol, keys)
        s += self.__semi__
    
    if hasattr(self, 'array'):
      s += ' ' + self.array.__pd__()

    return s
