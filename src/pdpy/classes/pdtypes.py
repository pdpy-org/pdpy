#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Pd Types Class Definitions """

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
  def __init__(self, value=None, name=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(json=json, xml=xml)
    if json is None and xml is None:
      self.value = self.__num__(value) if value is not None else None
      self.name = name
    
  def __pd__(self):
    return f"{self.value}"

  def __xml__(self):
    x = super().__element__(self)
    super().__subelement__(x, 'name', text=self.name)
    super().__subelement__(x, 'value', text=self.value)
    return x

class PdSymbol(PdFloat):
  """ A PdSymbol base class """
  def __init__(self, value=None, name=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(json=json, xml=xml)
    if json is None and xml is None:
      self.value = str(value) if value is not None else None
      self.name = name

class PdList(Base):
  """ A PdList base class """
  def __init__(self, name=None, json=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__()
    if json is not None:
      super().__populate__(self, json)
    else:
      self.name = name

  def addelement(self, e_type, e_key, e_value):
    """ Add a type to the list """
    
    if not hasattr(self, e_type):
      setattr(self, e_type, defaultdict(list))
    
    attr = getattr(self, e_type)

    e_value = self.__num__(e_value) if e_type == 'float' else str(e_value)
    
    attr[e_key].append(e_value)

  def __interleave__(self, s, attr, keys):
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
    for values in zip_longest(*[attr[k] for k in keys if k in attr], fillvalue=''):
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

  def __pd__(self, template):

    s = ''
    
    if hasattr(self, 'float') and hasattr(template, 'float'):
      keys = getattr(template, 'float')
      if keys:
        s = self.__interleave__(s, self.float, keys)
        s += self.__semi__
    
    if hasattr(self, 'symbol') and hasattr(template, 'symbol'):
      keys = getattr(template, 'symbol')
      if keys:
        s = self.__interleave__(s, self.symbol, keys)
        s += self.__semi__
    
    if hasattr(self, 'array'):
      s += ' ' + self.array.__pd__()

    return s

  def __xml__(self, template):
    """ Return the XML Element for this object """
    x = super().__element__(self)
    
    if hasattr(self, 'float') and hasattr(template, 'float'):
      keys = getattr(template, 'float')
      flt = super().__element__(tag='float')
      for k in keys:
        if k in self.float:
          for v in self.float[k]:
            super().__subelement__(flt, k, text=v)
      super().__subelement__(x, flt)

    if hasattr(self, 'symbol') and hasattr(template, 'symbol'):
      keys = getattr(template, 'symbol')
      sym = super().__element__(tag='symbol')
      for k in keys:
        if k in self.symbol:
          for v in self.symbol[k]:
            super().__subelement__(sym, k, text=v)
      super().__subelement__(x, sym)
    
    if hasattr(self, 'array') and hasattr(template, 'array'):
      for e, t in zip(getattr(self, 'array', []), template.array):
        _, _template = template.__parent__.getTemplate(t.template)
        super().__subelement__(x, e.__xml__(_template))
        # super().__subelement__(x, self.array.__xml__())
    
    return x
