#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Obj Class Definition """

from .object import Object

__all__ = [ 'Obj' ]

class Obj(Object):
  """ A Pure Data Obj object
  
  Description
  -----------
  This class represents a Pure Data object.

  Initialization Arguments
  ----------
  The first three arguments correspond to the `Object` class.
  1. `id`: The id of the pd object.
  2. `x`: The x-coordinate of the pd object.
  3. `y`: The y-coordinate of the pd object.
  4. `className`: The class name of the pd object.
  5. `args`: The argument `list` of the pd object.

  """
  def __init__(self, className=None, pd_lines=None, json=None, **kwargs):

    self.__pdpy__ = self.__class__.__name__
    super().__init__(json=json, **kwargs)

    if json is None and pd_lines is not None:
      super().__init__(*pd_lines[:3])
      try:
        self.className = pd_lines[3] if 3 < len(pd_lines) else ''
        if super().__isnum__(self.className):
          if 4 < len(pd_lines):
            self.className = 'list'
            self.addargs(pd_lines[3:])
          else:
            self.className = 'float'
            self.addargs(pd_lines[3])
        else:
          if 4 < len(pd_lines):
            self.addargs(pd_lines[4:])
      except:
        raise ValueError("Invalid arguments for Obj")
    
    if className is not None:
      self.className = className
    
    if not hasattr(self, 'className'):
      self.className = self.__cls__
  
  def __pd__(self, args=None):
    """ Return the pd code of the object. """
    if args is None:
      args = self.className
    else:
      args = self.className + ' ' + args
    # log(1, "Obj args:", args)
    return super().__pd__(args)

  def __xml__(self, args=None, **kwargs):
    """ Return the XML Element for this object. """

    attrib = kwargs.pop('attrib') if 'attrib' in kwargs else {}
    
    if 'scope' not in kwargs:
      kwargs.update({'scope':self})
    
    if 'tag' not in kwargs:
      kwargs.update({'tag':self.__cls__})
    
    kwargs.update({'attrib':attrib})

    return super().__xml__(classname=self.className, args=args, **kwargs)
