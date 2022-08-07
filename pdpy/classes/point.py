#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
""" Graphical Point Class Definitions """

from .base import Base

__all__ = ['Point']

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
    else:
      self.x = self.__d__.screen['x']
      self.y = self.__d__.screen['y']
    
  def __pd__(self):
    return str(self.x) + " " + str(self.y)

  def __xml__(self, tag=None):
    """ Return an XML Element """
    return super().__xml__(scope=self, tag=tag, attrib=('x', 'y'))

  def set_x(self, x):
    self.x = self.__num__(x)
    return self.x
  
  def set_y(self, y):
    self.y = self.__num__(y)
    return self.y

  def increment(self, x, y):
    self.x += x
    self.y += y