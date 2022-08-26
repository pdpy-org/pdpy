#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Class Definitions for the Old Graph Obj """

from ..core.base import Base
from ..primitives.area import Area # for the Graph class

__all__ = [ 'Graph' ]

class Graph(Base):
  """ The ye-olde array """
  def __init__(self, pd_lines=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(cls='graph')

    if pd_lines is not None:
      self.id = pd_lines[0]
      self.name = pd_lines[1]
      self.area = Area(pd_lines[2:6])
      self.range = Area(pd_lines[6:10])
    elif json is not None:
      super().__populate__(self, json)
    elif xml is not None:
      self.id = xml.findtext('id')
      self.name = xml.findtext('name')
      self.area = Area(xml=xml.find('area'))
      self.range = Area(xml=xml.find('range'))
 
  def addArray(self, *args):
    """ Append an array structure with symbols for name and template """
    if not hasattr(self, 'array'):
      self.array = []

    self.array.append({
      'name' : args[1],
      'length' : self.__num__(args[2]),
      'type' : args[3]
    })

  def __pd__(self):
    """ Returns the graph instruction for the pd file """
    s = self.name
    s += ' ' + self.range.__pd__(order=1)
    s += ' ' + self.area.__pd__(order=1)
    s = super().__pd__(s)
    for x in getattr(self, 'array', []):
      s += "#X array" + " " + str(x['name'])  + " " + str(x['length'])  + " " + str(x['type'])
      s += self.__end__
    s += '#X pop' + self.__end__
    return s

  def __xml__(self):
    """ Return the XML Element for this object """

    x = super().__xml__(scope=self, attrib=('name','area','range'))

    for a in getattr(self, 'array', []):
      arr = super().__element__(scope=a)
      for y in ('name', 'length', 'type'):
        super().__subelement__(arr, y, text=a[y])
      super().__subelement__(x, arr)
    return x

