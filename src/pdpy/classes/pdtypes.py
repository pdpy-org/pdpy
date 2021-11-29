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
  def __init__(self, value=None, name=None, json_dict=None):
    self.__pdpy__ = self.__class__.__name__
    if json_dict is not None:
      super().__populate__(self, json_dict)
    else:
      self.name = name
      self.value = value if value is not None else None

  def addelement(self, e_type, e_key, e_value):
    """ Add a type to the list """
    
    if not hasattr(self, e_type):
      setattr(self, e_type, defaultdict(list))
    
    attr = getattr(self, e_type)
    
    attr[e_key].append(e_value)


  def __pd__(self, template):
    s = ''
    
    # TODO: add support for more than one array template
    # leave this for now
    for i,t in enumerate(template.array):
      _, _template = template.__parent__.getTemplate(t.template)
    
    if i > 1:
      log(1, "Found more than one Array Template", template.__json__())
    
    def __interleave__(s, attr, keys):
      """
      interleave keys variable with attr
      zip_longest takes care of filling out the list with empty strings
      if these are of different lengths
      """
      for values in zip_longest(*[attr[k] for k in keys], fillvalue=''):
        for v in values:
          if isinstance(v, list):
            for val in v:
              if isinstance(v, list):
                s += ' '.join(val)
              else:
                s += f"{val} "
            s += ' \\;'
          else:
            s += ' ' + str(v)
        s += ' \\;'
      return s


    if hasattr(self, 'float') and hasattr(_template, 'float'):
      keys = getattr(_template, 'float')
      if keys:
        s = __interleave__(s, self.float, keys)
    
    if hasattr(self, 'symbol') and hasattr(_template, 'symbol'):
      keys = getattr(_template, 'symbol')
      if keys:
        s = __interleave__(s, self.symbol, keys)
    
    if hasattr(self, 'array'):
      s += ' ' + self.array.__pd__()

    return s + ' \\;'
