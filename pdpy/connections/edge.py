#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
"""
Edge
====
"""

from .iolet import Iolet
from ..core.base import Base
from ..utilities.utils import log

__all__ = [ 'Edge' ]

class Edge(Base):
  """ A Pd Connection 

  A Pd Connection object is a connection between two objects.

  Parameters
  ----------
  1. `source`: The source id of the connection
  2. `port`: The port outlet of the source
  3. `target`: The target id of the connection
  4. `port`: The port inlet of the target
  """
  def __init__(self, pd_lines=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(cls="connect", json=json, xml=xml)
    if pd_lines is not None and json is None and xml is None:
      self.source = Iolet(id=pd_lines[0], port=pd_lines[1]) 
      self.sink = Iolet(id=pd_lines[2], port=pd_lines[3])

  def connect(self):
    if not hasattr(self, '__p__'):
      log(1, "connect(): No parent Instance Attached")
    else:
      canvas = getattr(self,'__p__')
      # log(1, f"connect(): setting source")
      self.source.setobj(canvas)
      # log(1, f"connect(): setting sink")
      self.sink.setobj(canvas)
    return self

  def __pd__(self, o=None):
    # log(1,'EDGE to PD',self.__dict__)
    return super().__pd__(self.source.__pd__(o) + " " + self.sink.__pd__(o))

  def __xml__(self, o=None):
    """ Returns an xml element for this edge """
    x = super().__element__(scope=self)
    super().__subelement__(x, self.source.__xml__(o, tag='source'))
    super().__subelement__(x, self.sink.__xml__(o, tag='sink'))
    return x
