#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Class Definitions for Pure Data's Data Structures """

from . import goparray
from ..core.base import Base
from ..utilities.exceptions import ArgumentException
from ..utilities.utils import log

__all__ = [ 'Struct' ]

class Struct(Base):
  """ An object containing a Pure Data 'struct' header
  """
  def __init__(self, pd_lines=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    self.order = []
    super().__init__(pdtype='N', cls='struct')
    if json is not None: 
      super().__populate__(self, json)
    elif xml is not None:
      # log(1,xml.findall('*'))
      self.name = xml.findtext('name')
      # iterate through the attributes based on the order
      # order will be updated as we go
      for k,_ in sorted(xml.attrib.items(), key=lambda i: i[1]):
        e = k[:-1] # remove the 's'
        x = xml.find(k)
        if k=='floats':
          for s in x.findall(e): self.addFloat(s.text)
        elif k=='symbols':
          for s in x.findall(e): self.addSymbol(s.text)
        elif k=='texts':
          for s in x.findall(e): self.addText(s.text)
        elif k=='arrays':
          for s in x.findall('goparray'): 
            self.addArray(s.findtext('name'),s.findtext('template'))
        else:
          raise ArgumentException("Unknown attribute: {}".format(k))
  
    elif pd_lines is not None: 
      self.name = pd_lines[0]
      pd_lines = pd_lines[1:]
      i = 0
      while i < len(pd_lines):
        if i >= len(pd_lines): break
        pd_type = pd_lines[i]
        pd_name = pd_lines[i + 1]
        if   'float'  == pd_type: self.addFloat(pd_name)
        elif 'symbol' == pd_type: self.addSymbol(pd_name)
        elif 'text'   == pd_type: self.addText(pd_name)
        elif 'array'  == pd_type:
          array_name = pd_lines[i + 2]
          self.addArray(pd_name, array_name)
          i += 1
        else:
          log(1, "Unparsed Struct Field #" + str(i))
          log(1, self.name, pd_lines)
          self.__dumps__()
        i += 2
    else:
      pass
      # raise ArgumentException("Struct: Incorrect arguments given")
  
  def addFloat(self, pd_name):
    if not hasattr(self, 'float'):
      self.float = []
      self.order.append('float')
    self.float.append(pd_name)

  def addSymbol(self, pd_name):
    if not hasattr(self, 'symbol'):
      self.symbol = []
      self.order.append('symbol')
    self.symbol.append(pd_name)

  def addText(self, pd_name):
    if not hasattr(self, 'text'):
      self.text = []
      self.order.append('text')
    self.text.append(pd_name)

  def addArray(self, pd_name, array_name):
    """ Append an array structure with symbols for name and template """
    if not hasattr(self, 'array'):
      self.array = []
      self.order.append('array')
    self.array.append(goparray.GOPArray(json={
      'name' : pd_name,
      'template' : array_name
    }))

  def parse(self, data):
    """ Returns a list of scalar data structured by the corresponding struct """
    _data = {}
    # log(1,"DATA",data)
    # data = list(filter(lambda x:x==' ',data))
    if len(data) == 0: 
      return None
    arr = None
    fs = data[0].split(' ')
    # log(1,'FS',fs)
    if len(data) >= 2:
      arr = data[1:]
    # log(1,'ARR',arr)
    
    if hasattr(self, 'float'):
      _data.update({
        'float': {
            f:self.__num__(v) for f,v in zip(self.float, fs[:len(self.float)])
          }
      })
    if hasattr(self, 'symbol'):
      # log(1, "SYMBOLS", self.symbol, fs)
      _data.update({
        'symbol': {f:v for f,v in zip(self.symbol, fs[len(self.float):])}
      })
      # log(1, "DATA", _data)
    
    if arr is not None and hasattr(self, 'array'):
      for a in self.array:
        _, template = self.__parent__.getTemplate(a.template)
        
      if template is not None:
        if hasattr(template, 'float'):
          # fill the corresponding named arrays with float arrays
          _arr_obj = {}
          for val_list in arr:
            # zip key and value from template names and data float values
            for key, val in zip(template.float, val_list):
              if key in _arr_obj:
                _arr_obj[key].append(self.__num__(val))
              else:
                _arr_obj[key] = [self.__num__(val)]
          _data.update({
            'array' : _arr_obj
          })

        if hasattr(template, 'symbol'):
          # fill the corresponding named arrays with tring arrays
          _arr_obj = {}
          for val_list in arr:
            # zip key and value from template names and data string values
            for key, val in zip(template.symbol, val_list):
              if key in _arr_obj:
                _arr_obj[key].append(val)
              else:
                _arr_obj[key] = [val]
          _data.append(_arr_obj)
          
        if hasattr(template, 'array'):
          #TODO: implement this
          log(1,"DS recursion on arrays implemented")
    
    if len(_data):
      return _data

  def __pd__(self):
    """ Returns the struct instruction for the pd file """
    
    if not hasattr(self, 'name'):
      return self.__closeline__("X", "obj", self.position.__pd__() + " " + self.__cls__)

    s = self.name

    for a in getattr(self, 'order', []):
      arr = []
      for x in getattr(self, a, []):
        if a == 'array':
          x = x.__pd__()
        else:
          x = a + ' ' + x
        arr.append(x)
      s += ' ' + ' '.join(arr) if arr else ''
     
    return super().__pd__(s)
  
  def __xml__(self):
    """ Return the XML Element for this object """
    
    x = super().__xml__(self, attrib=('name'))
    
    for i,a in enumerate(getattr(self, 'order', [])):
      super().__update_attrib__(x, a + 's', i)
      xs = super().__element__(tag = a + 's')
      for e in getattr(self, a, []):
        if a == 'array':
          super().__subelement__(xs, e.__xml__())
        else: 
          super().__subelement__(xs, a, text=e)
      # update the parent elements
      super().__subelement__(x, xs)
    
    return x
