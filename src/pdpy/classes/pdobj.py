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

  def __pd__(self, args=None):
    """ Parses the pd object into a string """
    # add the position
    s = self.position.__pd__()
    # check if called with argumnts (array, text, etc) and append them
    if args:
      s += f" {args}"
    # check if we have extra arguments stored in the object and append them
    if hasattr(self, 'args'):
      for arg in self.args:
        s += f" {arg}"
    # wrap and close the pd line
    s = super().__pd__(s)
    
    # check if we have data and append it (this calls the PdData.__pd__ method)
    if hasattr(self, 'data'):
      s += self.data.__pd__()

    # return the pd line
    return s
