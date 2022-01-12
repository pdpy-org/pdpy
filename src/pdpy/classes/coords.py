#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
""" Graphical Coords Class Definitions """

from .base import Base
from .area import Area
from .point import Point
from .size import Size

__all__ = ['Coords']

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
