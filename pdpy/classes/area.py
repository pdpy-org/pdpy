#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
""" Graphical Area Class Definitions """

from .base import Base
from .point import Point

__all__ = ['Area']

class Area(Base):
  """ 
  Area
  ====
  
  Description
  -----------
  Represents an area with two points. See ::class::`Point`.
  The first two coordinates are the upper-left corner `a`,
  and the second two are the lower-right corner, `b`.
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
      return str(self.a.x) + " " + str(self.b.x) + " " + str(self.a.y) + " " + str(self.b.y)
    else:
      return self.a.__pd__() + " " + self.b.__pd__()

  def __xml__(self, tag=None):
    """ Return an XML Element """
    return super().__xml__(scope=self, tag=tag, attrib=('a', 'b'))
