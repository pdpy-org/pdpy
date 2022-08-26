#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021-22 Fede Camara Halac
# **************************************************************************** #
"""
Area
====
"""

from . import point
from ..core.base import Base

__all__ = [ 'Area' ]

class Area(Base):
  r""" Represents a rectangular section of the screen

  The area is represented with two points, ``a`` and ``b``.
  See :class:`pdpy.Point`.
  The first two coordinates are the upper-left corner in Point ``a``,
  and the second two are the lower-right corner in Point ``b``.
  
  ::
  
    a ────────────────────┐
    │                     │
    │                     │
    │                     │
    └──────────────────── b

  Parameters
  ----------

  coords : :class:`list`
    The list of 4 coordinates ``x1, y1, x2, y2`` (defaults: Point, Point)
  
  json : :class:`dict`
    The dictionary to populate the class

  xml : :class:`xml.etree.ElementTree.Element`
    The XML Element with two sub-elements for each point <a> and <b>

  Example
  -------
  
  This example imports and calls the class with the ``coords`` keywords

    >>> import pdpy_lib as pdpy
    >>> area = pdpy.Area(coords=[0,0,10,10])
  
  The default pd-lang string interleaves the coords, getting ``x1,x2,y1,y2``

    >>> area.__pd__()
    '0 10 0 10'

  If there is an ``order`` argument, coords remain the same: ``x1,y1,x2,y2``
  
    >>> area.__pd__(order=1)
    '0 0 10 10'

  The XML Element is accessed like this
  
    >>> area.__xml__()
    <Element 'area' at 0x1024379f0>

  """
  def __init__(self, coords=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__()
    if json is not None:
      super().__populate__(self, json)
    elif xml is not None:
      self.a = point.Point(xml=xml.find('a'))
      self.b = point.Point(xml=xml.find('b'))
    elif json is None and xml is None:
      self.a = point.Point(x=coords[0],y=coords[2]) if coords is not None else point.Point()
      self.b = point.Point(x=coords[1],y=coords[3]) if coords is not None else point.Point()
    
  def __pd__(self, order=0):
    """ Return the pd-lang string """
    if order == 1:
      return str(self.a.x) + " " + str(self.b.x) + " " + str(self.a.y) + " " + str(self.b.y)
    else:
      return self.a.__pd__() + " " + self.b.__pd__()

  def __xml__(self, tag=None):
    """ Return an XML Element """
    return super().__xml__(scope=self, tag=tag, attrib=('a', 'b'))
