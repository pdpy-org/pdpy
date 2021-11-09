#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

from .base import Base
from .data_structures import PdType, PdData

__all__ = [ 
  "Base",
  "Coords",
  "Graph",
  "Point",
  "PdObj"
  "Size"
]

class Point(Base):
  def __init__(self, x=None, y=None, json_dict=None, xml_object=None):
    self.__pdpy__ = self.__class__.__name__
    if x is not None and y is not None:
      self.x = self.num(x)
      self.y = self.num(y)
    elif isinstance(json_dict, dict):
      self.x = self.num(json_dict.get("x", None))
      self.y = self.num(json_dict.get("y", None))
    elif xml_object is not None:
      self.x = xml_object.findtext('x', None)
      self.y = xml_object.findtext('y', None)
    else:
      self.x = None
      self.y = None
class Size(Base):
  def __init__(self, w=None, h=None, json_dict=None, xml_object=None):
    self.__pdpy__ = self.__class__.__name__
    if w is not None and h is not None:
      self.width = self.num(w)
      self.height = self.num(h)
    elif isinstance(json_dict, dict):
      self.width = self.num(json_dict.get("width", 0))
      self.height = self.num(json_dict.get("height", 0))
    elif xml_object is not None:
      self.width = xml_object.findtext('width', 0)
      self.height = xml_object.findtext('height', 0)
    else:
      self.width = 0
      self.height = 0
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
    elif isinstance(json_dict, dict):
      self.lower = dtype(json_dict.get("lower", 0))
      self.upper = dtype(json_dict.get("upper", 0))
    elif xml_object is not None:
      self.lower = dtype(xml_object.findtext('lower', 0))
      self.upper = dtype(xml_object.findtext('upper', 0))
    else:
      self.lower = dtype(0)
      self.upper = dtype(0)

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
    elif isinstance(json_dict, dict):
      self.a = Point(json_dict=json_dict.get("a", None))
      self.b = Point(json_dict=json_dict.get("b", None))
    elif xml_object is not None:
      self.a = Point(xml_object=xml_object.find('a'))
      self.b = Point(xml_object=xml_object.find('b'))
    else:
      self.a = Point()
      self.b = Point()
  

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
    elif isinstance(json_dict, dict):
      self.range = Area(json_dict=json_dict.get("range", None))
      self.dimension = Size(json_dict=json_dict.get("dimension", None))
      self.gop = self.num(json_dict.get("gop", 0))
      if hasattr(json_dict, 'margin'):
        self.addmargin(json_dict=json_dict.get("margin", None))
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
  
class Graph(Base):
  def __init__(self, id, name, area, range):
    self.__pdpy__ = self.__class__.__name__
    self.id = id
    self.name = name
    self.area = Area(area)
    self.range = Area(range)
    self.array = []
    self.border = None
  
  def addArray(self, *argv):
    self.array.append(PdType(argv[0], size = argv[1]))

class PdObj(PdData):
  """ A PdObj base class 
  
  Description
  -----------
  A PdObj holds the id, and the x and y coordinates of the pd object,
  as well as the arguments array.

  Methods
  -------
  - `addargs(argv)`: Adds arguments to the pd object.
  """
  def __init__(self, id, x, y):
    self.__pdpy__ = self.__class__.__name__
    self.id = int(id)
    self.position = Point(x=x, y=y)
  
  def addargs(self, argv):
    if not hasattr(self,'args') or self.args is None: 
      self.args = []
    for arg in argv:
      self.args += [arg]
