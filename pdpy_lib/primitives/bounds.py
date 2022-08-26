#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
"""
Bounds
======
"""

from ..core.base import Base

__all__ = [ 'Bounds' ]

class Bounds(Base):
  """ Lower and upper bounds for GUI objects

  Parameters
  ----------

  lower : dtype or None
    The lower (minima) of the boundary (defaults: ``0``)

  upper : dtype or None
    The upper (maxima) of the boundary (defaults: ``0``)

  dtype : class
    Class to define bound value type (defaults: :class:`float`)

  json : :class:`dict` or None
    A json representation of the bounds class

  xml : :class:`xml.etree.ElementTree.Element` or None
    The XML Element with two sub-elements for each boundary <lower> and <upper>

  """
  def __init__(self, lower=None, upper=None, dtype=float, json=None, xml=None):
    
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
    """ Return the pd-lang string for the object. """
    return str(self.lower) + " " + str(self.upper)

  def __xml__(self, tag=None):
    """ Return an XML Element """
    return super().__xml__(scope=self, tag=tag, attrib=('lower', 'upper'))

