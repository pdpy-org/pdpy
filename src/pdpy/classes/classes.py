#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Graphical Class Definitions """

from .base import Base

__all__ = [
  "Point",
  "Size",
  "Bounds",
  "Area",
  "Coords"
]

class Point(Base):
  def __init__(self, x=None, y=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    if x is not None and y is not None:
      self.x = self.__num__(x)
      self.y = self.__num__(y)
    elif json is not None:
      super().__populate__(self, json)
    elif xml is not None:
      self.x = xml.findtext('x', None)
      self.y = xml.findtext('y', None)
    else:
      self.x = None
      self.y = None

  def __pd__(self):
    return f"{self.x} {self.y}"
class Size(Base):
  def __init__(self, w=None, h=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    if w is not None and h is not None:
      self.width = self.__num__(w)
      self.height = self.__num__(h)
    elif json is not None:
      super().__populate__(self, json)
    elif xml is not None:
      self.width = xml.findtext('width', 0)
      self.height = xml.findtext('height', 0)
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
               json=None,
               xml=None
               ):
    self.__pdpy__ = self.__class__.__name__
    if lower is not None and upper is not None:
      self.lower = dtype(lower)
      self.upper = dtype(upper)
    elif json is not None:
      super().__populate__(self, json)
    elif xml is not None:
      self.lower = dtype(xml.findtext('lower', 0))
      self.upper = dtype(xml.findtext('upper', 0))
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
  def __init__(self, coords=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    if coords is not None:
      self.a = Point(x=coords[0], y=coords[2])
      self.b = Point(x=coords[1], y=coords[3])
    elif json is not None:
      super().__populate__(self, json)
    elif xml is not None:
      self.a = Point(xml=xml.find('a'))
      self.b = Point(xml=xml.find('b'))
    else:
      self.a = Point()
      self.b = Point()
  
  def __pd__(self, order=0):
    if order == 1:
      return f"{self.a.x} {self.b.x} {self.a.y} {self.b.y}"
    else:
      return f"{self.a.x} {self.a.y} {self.b.x} {self.b.y}"


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
  def __init__(self, coords=None, json=None, xml=None):
    
    self.__pdpy__ = self.__class__.__name__
    super().__init__(cls='coords')
    
    if json is not None:
      super().__populate__(self, json)
    
    elif coords is not None:
      # NON-GOP
      self.range = Area(coords=coords[:4])
      self.dimension = Size(w=coords[4], h=coords[5])
      self.gop = self.__num__(coords[6])
      # GOP
      if 9 == len(coords):
        self.addmargin(x=coords[7], y=coords[8])
    
    elif xml is not None:
      self.range = Area(xml=xml.find('range'))
      self.dimension = Size(xml=xml.find('dimension'))
      self.gop = self.__num__(xml.findtext("gop", 0))
      if xml.find('margin'):
        self.addmargin(xml=xml.find('margin'))
    else:
      self.range = Area()
      self.dimension = Size()
      self.gop = 0
      self.margin = Size()

  def addmargin(self, **kwargs):
    self.margin = Point(**kwargs)
  
  def __pd__(self):
    s = f"{self.range.__pd__()} {self.dimension.__pd__()} {self.gop}"
    if hasattr(self, 'margin'):
      s += f" {self.margin.__pd__()}"
    return super().__pd__(s)
