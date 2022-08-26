#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
""" Graphical Size Class Definitions """

from ..core.base import Base

__all__ = ['Size']

class Size(Base):
  def __init__(self, w=None, h=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__()
    if json is not None:
      super().__populate__(self, json)
    if xml is not None:
      self.width = self.__num__(xml.findtext('w'))
      self.height = self.__num__(xml.findtext('h'))
    if w is not None:
      self.width  = self.__num__(w) if w is not None else None
    if h is not None:
      self.height = self.__num__(h) if h is not None else None
  
    

  def __pd__(self):
    s = ''
    if hasattr(self, 'width'):
      s += str(self.width)
    if hasattr(self, 'width') and hasattr(self, 'height'):
      s += ' '
    if hasattr(self, 'height'):
      s += str(self.height)
    return s
  
  def __xml__(self, tag=None):
    """ Return an XML Element """
    return super().__xml__(scope=self, tag=tag, attrib=('width', 'height'))

  def set_width(self, width):
    self.width = self.__num__(width)
    return self.width
  
  def set_height(self, height):
    self.height = self.__num__(height)
    return self.height