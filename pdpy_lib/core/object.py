#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Object Class Definitions """

from . import base
from ..primitives.point import Point

__all__ = [ 'Object' ]

class Object(base.Base):
  """ A Object base class 
  
  A Object holds the id, and the x and y coordinates of the pd object,
  as well as the arguments array.

  Methods
  -------
  - `addargs(argv)`: Adds arguments to the pd object.
  """
  def __init__(self, id=None, x=None, y=None, **kwargs):

    self.__pdpy__ = self.__class__.__name__
    if id is not None:
      self.id = int(id)
    self.position = Point(x=x, y=y)
    super().__init__(**kwargs)
  
  def addargs(self, *argv):
    if not hasattr(self,'args') or self.args is None: 
      self.args = []
    self.args += self.__unescape__(argv)
    return self

  def __pd__(self, args=None):
    """ Parses the pd object into a string """

    # add the position
    s = self.position.__pd__()
    # check if called with argumnts (array, text, etc) and append them
    if args is not None:
      s += " " + str(args)
    # check if we have extra arguments stored in the object and append them
    for arg in getattr(self, 'args', []):
      # print('arg:',repr(arg))
      
      if arg is None: 
        continue
      
      if type(arg) in (float, int):
        argument = str(arg)
      elif arg == ' ' or all([a==' ' for a in arg]):
        argument = self.__escape__(arg)
      else:
        arg = arg.split(' ')
        argument = ' '.join(map(lambda x: ' ' + self.__escape__(x),arg))
      # print('argument:',repr(arg))
      s += " " + argument
    # wrap and close the pd line
    s = super().__pd__(s)
    # print("pd_line:", s)
    
    # check if we have data and append it (this calls the Data.__pd__ method)
    for x in getattr(self, 'data', []):
      s += x.__pd__()

    # return the pd line
    return s

  def __xml__(self, classname=None, args=None, **kwargs):
    """ Returns an XML Element for this object """
    # print("obj",classname, args, kwargs)
    x = super().__xml__(**kwargs)

    super().__update_element__(x, self, ('id', 'position'))
    
    if hasattr(self, 'args'):
      a = super().__element__(tag='args')
      for _arg in getattr(self, 'args', []):
        super().__subelement__(a, 'arg', text=_arg)
      super().__subelement__(x, a)
    
    if hasattr(self, 'data'):
      data = super().__element__(tag='data')
      for d in getattr(self, 'data', []):
        super().__subelement__(data, d.__xml__())
      super().__subelement__(x, data)
    
    if classname is not None:
      super().__subelement__(x, 'className', text=classname)
    if args is not None:
      super().__subelement__(x, 'arguments', text=args)
    
    return x
  
  def move(self, x=None, y=None):
    """ Move the object to a new position. """
    if x is not None:
      self.position.set_x(x)
    if y is not None:
      self.position.set_y(y)
