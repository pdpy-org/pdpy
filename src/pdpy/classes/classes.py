#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
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
    super().__init__()
    if json is not None:
      super().__populate__(self, json)
    elif xml is not None:
      self.x = self.__num__(xml.findtext('x'))
      self.y = self.__num__(xml.findtext('y'))
    elif json is None and xml is None:
      self.x = self.__num__(x) if x is not None else None
      self.y = self.__num__(y) if y is not None else None
    
  def __pd__(self):
    return f"{self.x} {self.y}"

  def __xml__(self, tag=None):
    """ Return an XML Element """
    return super().__xml__(scope=self, tag=tag, attrib=('x', 'y'))

class Size(Base):
  def __init__(self, w=None, h=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__()
    if json is not None:
      super().__populate__(self, json)
    elif xml is not None:
      self.w = self.__num__(xml.findtext('w'))
      self.h = self.__num__(xml.findtext('h'))
    elif json is None and xml is None:
      self.width  = self.__num__(w) if w is not None else None
      self.height = self.__num__(h) if h is not None else None
    
  def __pd__(self):
    s = ''
    if hasattr(self, 'width'):
      s += f"{self.width}"
    if hasattr(self, 'width') and hasattr(self, 'height'):
      s += ' '
    if hasattr(self, 'height'):
      s += f"{self.height}"
    return s
  
  def __xml__(self, tag=None):
    """ Return an XML Element """
    return super().__xml__(scope=self, tag=tag, attrib=('width', 'height'))

class Bounds(Base):
  def __init__(self,
               lower=None,
               upper=None,
               dtype=float,
               json=None,
               xml=None
               ):
    self.__pdpy__ = self.__class__.__name__
    super().__init__()
    if json is not None:
      super().__populate__(self, json)
    elif xml is not None:
      self.lower = dtype(xml.findtext('lower'))
      self.upper = dtype(xml.findtext('upper'))
    elif json is None and xml is None:
      self.lower = dtype(lower) if lower is not None else dtype(0)
      self.upper = dtype(upper) if upper is not None else dtype(0)

  def __pd__(self):
    return f"{self.lower} {self.upper}"

  def __xml__(self, tag=None):
    """ Return an XML Element """
    return super().__xml__(scope=self, tag=tag, attrib=('lower', 'upper'))

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
    super().__init__()
    if json is not None:
      super().__populate__(self, json)
    elif xml is not None:
      self.a = Point(xml=xml.find('a'))
      self.b = Point(xml=xml.find('b'))
    elif json is None and xml is None:
      self.a = Point(x=coords[0],y=coords[2]) if coords is not None else Point()
      self.b = Point(x=coords[1],y=coords[3]) if coords is not None else Point()
    
  def __pd__(self, order=0):
    if order == 1:
      return f"{self.a.x} {self.b.x} {self.a.y} {self.b.y}"
    else:
      return f"{self.a.__pd__()} {self.b.__pd__()}"

  def __xml__(self, tag=None):
    """ Return an XML Element """
    return super().__xml__(scope=self, tag=tag, attrib=('a', 'b'))

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
    super().__init__(cls='coords', json=json, xml=xml)
    super().__init__()
    if json is not None:
      super().__populate__(self, json)
    elif xml is not None:
      self.range = Area(xml=xml.find('range'))
      self.dimension = Size(xml=xml.find('dimension'))
      self.gop = self.__num__(xml.findtext('gop', 0))
      if xml.find('margin'):
        self.addmargin(xml=xml.find('margin'))
    elif json is None and xml is None:
      # NON-GOP
      self.range = Area(coords=coords[:4]) if coords is not None else Area()
      self.dimension = Size(w=coords[4], h=coords[5]) if coords is not None else Size()
      self.gop = self.__num__(coords[6]) if coords is not None else 0
      # GOP
      if 9 == len(coords):
        self.addmargin(x=coords[7], y=coords[8])

  def addmargin(self, **kwargs):
    self.margin = Point(**kwargs)
  
  def __pd__(self):
    s = f"{self.range.__pd__(order=1)} {self.dimension.__pd__()} {self.gop}"
    if hasattr(self, 'margin'):
      s += f" {self.margin.__pd__()}"
    return super().__pd__(s)

  def __xml__(self, tag=None):
    """ Return an XML Element """
    return super().__xml__(scope=self, tag=tag, attrib=('range', 'dimension', 'gop', 'margin'))
