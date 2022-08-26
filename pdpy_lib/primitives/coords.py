#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
"""
Coords
======
"""

from . import area, point, size
from ..core.base import Base

__all__ = ['Coords']

class Coords(Base):
  """ Coordinates of a Pd Patch

  The coordinates of the Pd Patch takes a list of 7 or 9 arguments 
  Created in the following format:
  - `range` : first 4 floats are the Area. Defined by 2 Points. See :class:`Area` and :class:`Point`.
  - `dimension` : next 2 floats are the Size. See :class:`Size`.
  - `gop` : next 1 int (0 or 1) defines if it must Graph-on-Parent.
  - `margin` : if present, next 2 floats are the margins. See :func:`addmargin`)

  """
  def __init__(self, coords=None, json=None, xml=None, **kwargs):
    
    self.__pdpy__ = self.__class__.__name__
    super().__init__(cls='coords', json=json, xml=xml)
    if json is not None:
      super().__populate__(self, json)
    elif xml is not None:
      self.range = area.Area(xml=xml.find('range'))
      self.dimension = size.Size(xml=xml.find('dimension'))
      self.gop = self.__num__(xml.findtext('gop', 0))
      if xml.find('margin'):
        self.addmargin(xml=xml.find('margin'))
    elif json is None and xml is None and coords is not None:
      # NON-GOP
      self.range = area.Area(coords=coords[:4]) if coords is not None else area.Area()
      self.dimension = size.Size(w=coords[4], h=coords[5]) if coords is not None else size.Size()
      self.gop = self.__num__(coords[6]) if coords is not None else 0
      # GOP
      if 9 == len(coords):
        self.addmargin(x=coords[7], y=coords[8])
    else:
      if 'gop' in kwargs:
        self.gop = kwargs.pop('gop')
      else:
        self.gop = self.__d__.coords['gop']
      if 'range' in kwargs:
        self.range = area.Area(kwargs.pop('area'))
      else:
        self.range = area.Area(coords=[
          self.__d__.coords['range']['xmin'],
          self.__d__.coords['range']['ymax'],
          self.__d__.coords['range']['xmax'],
          self.__d__.coords['range']['ymin']]
        )
      if 'dimen' in kwargs:
        self.dimension = size.Size(kwargs.pop('dimen'))
      else:
        self.dimension = size.Size(
          w = self.__d__.coords['dimen']['width'],
          h = self.__d__.coords['dimen']['height']
        )
      
      if self.gop:
        if 'margin' in kwargs:
          self.addmargin(kwargs.pop('margin'))
        else:
          self.addmargin(
            x = self.__d__.coords['margin']['x'],
            y = self.__d__.coords['margin']['y']
          )


  def addmargin(self, **kwargs):
    """ Adds the margins to the coords class """
    self.margin = point.Point(**kwargs)
  
  def __pd__(self):
    """ Returns the pd-lang string for the coordinates """
    s = self.range.__pd__(order=1) + " " + self.dimension.__pd__() + " " + str(self.gop)
    if hasattr(self, 'margin'):
      s += " " + self.margin.__pd__()
    return super().__pd__(s)

  def __xml__(self, tag=None):
    """ Return an XML Element """
    return super().__xml__(scope=self, tag=tag, attrib=('range', 'dimension', 'gop', 'margin'))
