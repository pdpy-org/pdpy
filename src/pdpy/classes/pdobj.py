#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

from .data_structures import PdData
from .classes import Point

__all__ = [
  "PdObj"
]

class PdObj(PdData):
  """ A PdObj base class 
  
  Description
  -----------
  A PdObj holds the id, and the x and y coordinates of the pd object,
  as well as the arguments array.

  Methods
  -------
  - `addargs(argv)`: Adds arguments to the pd object.
  """
  def __init__(self, id, x, y, **kwargs):
    self.__pdpy__ = self.__class__.__name__
    self.id = int(id)
    self.position = Point(x=x, y=y)
    super().__init__(**kwargs)
  
  def addargs(self, argv):
    if not hasattr(self,'args') or self.args is None: 
      self.args = []
    for arg in argv:
      self.args += [arg]
