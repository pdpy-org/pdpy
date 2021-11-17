#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

from .base import Base
from .classes import Point

__all__ = [
  "PdObj"
]

class PdObj(Base):
  """ A PdObj base class 
  
  Description
  -----------
  A PdObj holds the id, and the x and y coordinates of the pd object,
  as well as the arguments array.

  Methods
  -------
  - `addargs(argv)`: Adds arguments to the pd object.
  """
  def __init__(self, id=None, x=None, y=None, **kwargs):

    self.__pdpy__ = self.__class__.__name__
    if id is not None:
      self.id = int(id)
    if x is not None and y is not None:
      self.position = Point(x=x, y=y)
    super().__init__(**kwargs)
  
  def addargs(self, argv):
    if not hasattr(self,'args') or self.args is None: 
      self.args = []
    for arg in argv:
      self.args += [arg]

  def __pd__(self):
    """ Parses the pd object into a string """
    s = self.position.__pd__()
    if hasattr(self, 'args'):
      for arg in self.args:
        s += f" {arg}"
    return super().__pd__(s)
