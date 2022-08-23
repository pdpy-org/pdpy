#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Pd Types Class Definitions """

from collections import defaultdict
from itertools import zip_longest
from ..core.base import Base

__all__ = [
  'Int',
  'Float',
  'Symbol',
  'List',
]

class Float(Base):
  """ A Float base class """
  def __init__(self, value=None, name=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__()
    if xml is not None:
      self.name = xml.findtext('name')
      self.value = self.__num__(xml.findtext('value'))
    elif json is not None:
      super().__populate__(self, json=json)
    elif json is None and xml is None:
      self.value = self.__num__(value) if value is not None else None
      self.name = name
  
  def __pd__(self):
    return str(getattr(self, 'value', ''))

  def __xml__(self):
    x = super().__element__(scope=self)
    super().__subelement__(x, 'name', text=self.name)
    super().__subelement__(x, 'value', text=self.value)
    return x

class Symbol(Float):
  """ A Symbol base class """
  def __init__(self, value=None, name=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__()
    if xml is not None:
      self.name = xml.findtext('name')
      self.value = xml.findtext('value')
    elif json is not None:
      super().__populate__(self, json=json)
    elif json is None and xml is None:
      self.value = str(value) if value is not None else None
      self.name = name

class Int(Float):
  """ A Int base class """
  def __init__(self, value=None, name=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__()
    if xml is not None:
      self.name = xml.findtext('name')
      self.value = xml.findtext('value')
    elif json is not None:
      super().__populate__(self, json=json)
    elif json is None and xml is None:
      self.value = int(value) if value is not None else None
      self.name = name

class List(Base):
  """ A List base class """
  def __init__(self, name=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__()
    if xml is not None:
      self.name = xml.findtext('name')
      for e_type in ('float', 'symbol', 'array'):
        if xml.find(e_type):
          for x in xml.find(e_type).findall('*'):
            self.addelement(e_type, x.tag, x.text)
    elif json is not None:
      super().__populate__(self, json)
    else:
      self.name = name

  def addelement(self, e_type, e_key, e_value):
    """ Add a type to the list """
    # log(1, f"e_type:{e_type}, e_key:{e_key}, e_value:{e_value}")
    
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
              s += str(val) + " "
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
    x = super().__element__(scope=self)
    
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
