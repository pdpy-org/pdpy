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
    # log(1, "PdObj args:", args)
    
    # add the position
    s = self.position.__pd__()
    # check if called with argumnts (array, text, etc) and append them
    if args:
      s += f" {args}"
    # check if we have extra arguments stored in the object and append them
    for x in getattr(self, 'args', []):
      s += f" {x}"
    # wrap and close the pd line
    s = super().__pd__(s)
    
    # check if we have data and append it (this calls the PdData.__pd__ method)
    for x in getattr(self, 'data', []):
      s += x.__pd__()

    # return the pd line
    return s


  def __xml__(self, subclass=None, args=None):
    """ Returns an XML Element for this object """
    x = super().__element__(self)
    super().__subelement__(x, self.position.__xml__())
    if subclass is not None:
      super().__subelement__(x, 'subclass', subclass)
    if args is not None:
      super().__subelement__(x, 'arguments', args)
    for e in getattr(self, 'args', []):
      super().__subelement__(x, 'arg', text=e)
    for e in getattr(self, 'data', []):
      super().__subelement__(x, e.__xml__())
    return x
