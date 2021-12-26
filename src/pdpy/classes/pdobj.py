#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" PdObj Class Definitions """

from .base import Base
from .classes import Point

__all__ = [ 'PdObj' ]

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
    if not isinstance(argv, list):
      argv = [argv]
    self.args += argv

  def __pd__(self, args=None):
    """ Parses the pd object into a string """
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


  def __xml__(self, classname=None, args=None, **kwargs):
    """ Returns an XML Element for this object """
    # print("pdobj",classname, args, kwargs)
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
    
    # if hasattr(self, 'data'):
      # for d in getattr(self, 'data', []):
        # data = super().__element__(tag='data')
        # data.set('header', getattr(d, 'header'))
        # for datum in getattr(d, 'data', []):
        #   if not isinstance(datum, list) and not isinstance(datum, tuple):
        #     super().__subelement__(data, 'datum', text=datum)
        #   else:
        #     data_mult = super().__element__('data')
        #     for dd in datum:
        #       super().__subelement__(data_mult, 'datum', text=dd)
        #     super().__subelement__(data, data_mult)
        # super().__subelement__(x, data)
    
    if classname is not None:
      super().__subelement__(x, 'className', text=classname)
    elif 'tag' in kwargs:
      super().__subelement__(x, 'className', text=kwargs.pop('tag'))
    if args is not None:
      super().__subelement__(x, 'arguments', text=args)
    
    return x
