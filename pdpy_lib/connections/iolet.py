#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
"""
Iolet
=====
"""

from ..core.base import Base
from ..utilities.utils import log

__all__ = [ 'Iolet' ]

class Iolet(Base):
  def __init__(self, id=None, port=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(json=json, xml=xml)
    if json is None and xml is None:
      self.id = id
      self.port = port
    # cast to int
    self.id = int(self.id)
    self.port = int(self.port)
  
  def setobj(self, parent):
    """ Locates the node in the parent (Canvas) object """
    for obj in getattr(parent, 'nodes', []):
      if getattr(obj, 'id') == self.id:
        setattr(self, '__obj__', obj) # update with a new attribute
    # log(1, f"setobj()::{self.__dict__}")
    

  def __remap__(self, obj_map):
    """ Get the value from the mapped indices """
    # query the map for the value at the id key
    if self.id in obj_map:
      return str(obj_map.get(self.id))
    else:
      log(1, "__remap__()::Key Not Found" + " " + str(self.id))
      return self.id

  def __pd__(self, obj_map=None):
    """ Returns a pd string for this source """
    if not hasattr(self, '__obj__'):
      return str(self.__remap__(obj_map) if obj_map else self.id)  + " " + str(self.port)
    else:
      return str(self.__obj__.id) + " " + str(self.port)
  
  def __xml__(self, obj_map=None, tag=None):
    """ Returns an xml element for this source """
    x = super().__element__(scope=self, tag=tag)
    super().__subelement__(x, 'id', text = self.id)
    super().__subelement__(x, 'port', text = self.port)
    return x
