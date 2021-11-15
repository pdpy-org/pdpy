#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

from .base import Base
from .data_structures import PdType

__all__ = [ 
  "Base",
  "Coords",
  "Graph",
  "Point",
  "Size",
  "Bounds",
  "Area",
  "ArgumentException"
]

class ArgumentException(Exception):
  pass

class Point(Base):
  def __init__(self, x=None, y=None, json_dict=None, xml_object=None):
    self.__pdpy__ = self.__class__.__name__
    if x is not None and y is not None:
      self.x = self.num(x)
      self.y = self.num(y)
    elif json_dict is not None:
      super().__populate__(self, json_dict)
    elif xml_object is not None:
      self.x = xml_object.findtext('x', None)
      self.y = xml_object.findtext('y', None)
    else:
      self.x = None
      self.y = None

  def __pd__(self):
    return f"{self.x} {self.y}"
class Size(Base):
  def __init__(self, w=None, h=None, json_dict=None, xml_object=None):
    self.__pdpy__ = self.__class__.__name__
    if w is not None and h is not None:
      self.width = self.num(w)
      self.height = self.num(h)
    elif json_dict is not None:
      super().__populate__(self, json_dict)
    elif xml_object is not None:
      self.width = xml_object.findtext('width', 0)
      self.height = xml_object.findtext('height', 0)
    else:
      self.width = 0
      self.height = 0

  def __pd__(self):
    return f"{self.width} {self.height}"

class Bounds(Base):
  def __init__(self,
               lower=None,
               upper=None,
               dtype=float,
               json_dict=None,
               xml_object=None
               ):
    self.__pdpy__ = self.__class__.__name__
    if lower is not None and upper is not None:
      self.lower = dtype(lower)
      self.upper = dtype(upper)
    elif json_dict is not None:
      super().__populate__(self, json_dict)
    elif xml_object is not None:
      self.lower = dtype(xml_object.findtext('lower', 0))
      self.upper = dtype(xml_object.findtext('upper', 0))
    else:
      self.lower = dtype(0)
      self.upper = dtype(0)
  
  def __pd__(self):
    return f"{self.lower} {self.upper}"
class Area(Base):
  """ 
  Area
  ====
  
  Description
  -----------
  Represents an area with two points. See ::class::`Point`.
  The first two coordinates are the upper left corner `a`,
  and the second two are the upper lower corner, `b`.
  a ------------------- |
  |                     |
  |                     |
  |                     v
  |-------------------> b
  """
  def __init__(self, coords=None, json_dict=None, xml_object=None):
    self.__pdpy__ = self.__class__.__name__
    if coords is not None:
      self.a = Point(x=coords[0], y=coords[1])
      self.b = Point(x=coords[2], y=coords[3])
    elif json_dict is not None:
      super().__populate__(self, json_dict)
    elif xml_object is not None:
      self.a = Point(xml_object=xml_object.find('a'))
      self.b = Point(xml_object=xml_object.find('b'))
    else:
      self.a = Point()
      self.b = Point()
  
  def __pd__(self):
    return f"{self.a.x} {self.b.x} {self.a.y} {self.b.y}"

class Coords(Base):
  """ 
  Coordinates of the Pd Patch
  ===========================

  Description
  ----------
  The coordinates of the Pd Patch takes a list of 7 or 9 arguments 
  Created in the following format:
  - `range` : first 4 floats are the Area. Defined by 2 Points. See ::class::`Area` and ::class::`Point`.
  - `dimension` : next 2 floats are the Size. See ::class::`Size`.
  - `gop` : next 1 int (0 or 1) defines if it must Graph-on-Parent.
  - `margin` : if present, next 2 floats are the margins. See ::func::`addmargin`)

  """
  def __init__(self, coords=None, json_dict=None, xml_object=None):
    self.__pdpy__ = self.__class__.__name__
    if coords is not None:
      # NON-GOP
      self.range = Area(coords=coords[:4])
      self.dimension = Size(w=coords[4], h=coords[5])
      self.gop = self.num(coords[6])
      # GOP
      if 9 == len(coords):
        self.addmargin(x=coords[7], y=coords[8])
    elif json_dict is not None:
      super().__populate__(self, json_dict)
    elif xml_object is not None:
      self.range = Area(xml_object=xml_object.find('range'))
      self.dimension = Size(xml_object=xml_object.find('dimension'))
      self.gop = self.num(xml_object.findtext("gop", 0))
      if xml_object.find('margin'):
        self.addmargin(xml_object=xml_object.find('margin'))
    else:
      self.range = Area()
      self.dimension = Size()
      self.gop = 0
      self.margin = Size()

  def addmargin(self, **kwargs):
    self.margin = Point(**kwargs)
  
  def __pd__(self):
    return f" {self.range.__pd__()} {self.dimension.__pd__()} {self.gop} " + self.margin.__pd__() if self.margin else ""

class Graph(Base):
  def __init__(self, pd_lines=None, json_dict=None, xml_object=None):
    self.__pdpy__ = self.__class__.__name__
    if pd_lines is not None:
      self.id = pd_lines[0]
      self.name = pd_lines[1]
      self.area = Area(pd_lines[2:5])
      self.range = Area(pd_lines[5:8])
      self.array = []
      self.border = None
    elif json_dict is not None:
      super().__populate__(self, json_dict)
    elif xml_object is not None:
      self.id = xml_object.findtext('id')
      self.name = xml_object.findtext('name')
      self.area = Area(xml_object=xml_object.find('area'))
      self.range = Area(xml_object=xml_object.find('range'))
      self.array = []
      self.border = None
  
  def addArray(self, *argv):
    self.array.append(PdType(json_dict={
      'name' : argv[0],
      'size' : argv[1]
    }))


