#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" PdPyXMLParser Class Definition """

import json
import xml.etree.ElementTree as ET
from io import IOBase
from .. import utilities

__all__ = [ 'PdPyXMLParser' ]

class PdPyXMLParser:

  def __init__(self, parent, xml):
    self.elements = list(list())
    self.depth = 0
    # the pdpy module namespace
    self.__n__ = utilities.Namespace()
    # the parser object to which we pass this class as target
    parser = ET.XMLParser(target=self)
    
    # check if the xml is a file or a string
    if isinstance(xml, IOBase):
      # if it is a file, parse it, the `target` takes care of the rest
      ET.parse(xml, parser=parser)
    else:
      print("__init__(): xml is a string:", xml)

  def __check__(self, tag, attrib):
    __pdpy__ = self.__n__.get(name=getattr(attrib, 'pdpy', None), tag=tag)
    if __pdpy__ is None:
      raise KeyError("No PdPy class found for element: " + tag)
    return __pdpy__

  def start(self, tag, attrib):
    # print('start:',tag, attrib)
    obj = {
      'tag':tag,
      'attrib':attrib,
      'isobj':isinstance(self.__check__(tag, attrib), type),
      'json': []
    }
    print(obj)
    self.elements.append(obj)
  
  def data(self, data):
    # print('data:',data)
    data = data.strip() # remove whitespace
    # only add data if it is not empty 
    if data is not None and data != '':
      self.elements[-1].update({'data':data})
      
  def end(self, tag):
    # print('end:',tag)
    # decrement depth
    if len(self.elements) > 1:
      elem = self.elements.pop()
      
      for i in range(len(self.elements)-1, 0, -1):
        print(self.elements[i])
        if self.elements[i]['isobj']:
          self.elements[i]['json'].append(elem)
          break

  def close(self):
    # print('close')
    print("*"*80)
    print(json.dumps(self.elements, indent=2))
