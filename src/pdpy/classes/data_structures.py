#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions for Pure Data's Data Structures """

from .base import Base
from .default import GOPArrayFlags
from ..util.utils import  log, splitByEscapedChar

__all__ = [
  "Scalar", 
  "Struct",
  "PdData",
  "PdType"
]

class PdData(Base):
  def __init__(self):
    self.__pdpy__ = self.__class__.__name__
    self.data = []
    return self
  
  def addData(self, data, dtype=float, char=None):
    if char is not None:
      self.data = splitByEscapedChar(data, char=char)
    else:
      self.data = [dtype(d) for d in data]

class PdType(PdData):
  def __init__(self, name, template=None, size=None, flag=None, className=None):
    self.__pdpy__ = self.__class__.__name__
    self.name = name
    self.template = template
    self.size = self.num(size) if size is not None else None
    self.flag = GOPArrayFlags[int(flag)] if flag is not None and flag.isnumeric() else None
    self.className = className

class Struct(Base):
  """ An object containing a Pure Data 'struct' header
  """
  def __init__(self, *argv, source='pd'):
    self.__pdpy__ = self.__class__.__name__
    
    if   source == 'pd'   : self.parsePd(argv)
    elif source == 'json' : pass
    elif source == 'xml'  : self.parseXML(argv[0])
    elif source == 'pdpy' : pass
    else: 
      log(1, f"Unsupported source: {source}")

  def parsePd(self, argv):
    self.name = argv[0]
    argv = argv[1:]
    
    i = 0

    while i < len(argv):
      if i >= len(argv): break
      pd_type = argv[i]
      pd_name = argv[i + 1]
      
      if   'float'  == pd_type: self.addFloat(pd_name)
      elif 'symbol' == pd_type: self.addSymbol(pd_name)
      elif 'text'   == pd_type: self.addSymbol(pd_name)
      elif 'array'  == pd_type:
        i += 2
        self.addArray(pd_name, argv[i])
      else:
        # log(1, self.name, argv)
        log(1, f"Unparsed Struct Field #{i}")
      
      i += 2
  
  def parseXML(self, x):
    # x is the xml object
    # log(1,x.findall('*'))
    self.name = x.findtext('name')
    for s in x.findall('float'): self.addFloat(s.text)
    for s in x.findall('symbol'): self.addSymbol(s.text)
    for s in x.findall('text'): self.addSymbol(s.text)
    for s in x.findall('array'): 
      self.addArray(s.findtext('name'),s.findtext('template'))
  
  def addFloat(self, pd_name):
    if not hasattr(self, 'float'):
      self.float = []
    self.float.append(pd_name)

  def addSymbol(self, pd_name):
    if not hasattr(self, 'symbol'):
      self.symbol = []
    self.symbol.append(pd_name)

  def addArray(self, pd_name, array_name):
    if not hasattr(self, 'array'):
      self.array = []
    self.array.append(PdType(pd_name, array_name))

class Scalar(PdData):
  def __init__(self, struct, name, *data, source='pd'):
    self.__pdpy__ = self.__class__.__name__
    self.className = "scalar"
    self.name = name
    if source=='pd':
      self.parsePd(struct, data)
    elif source=='json':
      self.parseJson(struct, data)

  def parseJson(self, struct, data):
    for s in struct:
      if self.name == s.name:
        super().addData(data)
  
  def parsePd(self, struct, data):
    for s in struct:
      if self.name == s.name:
        # print('parsing struct', data)
        super().addData(data, char=";")

