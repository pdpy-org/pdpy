#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Class Definitions """

from .connections import Comm
from .object import Object
from .bounds import Bounds

__all__ = [ 'Gui' ]

class Gui(Object):
  """ A Pd Native Gui object 
  
  Description
  -----------
  A Pd Native Gui object is a graphical user interface that is implemented in
  pure data. It is a sublcass of the `Object`

  Initialization Arguments
  -----------------------
  1. `className`: the name of the class of the object
  2. id: The id of the object
  3. `x`: The x position of the object
  4. `y`: The y position of the object
  5. `digits_width` : The width of the object in digits
  6. lower limit: The lower limit of the object
  7. upper limit: The upper limit of the object
  8. `flag`: The flag of the object
  9. `label`: The label of the object
  10. `receive`: the receiver symbol of the object
  11. `send`: the sender symbol of the object

  """
  def __init__(self, pd_lines=None, json=None):

    super().__init__(json=json)
    
    if json is None:
      cls = pd_lines.pop(0)
      super().__init__(*pd_lines[:3], cls=cls)
      self.__pdpy__ = self.__class__.__name__
      self.className = self.__cls__
      if 3 < len(pd_lines):
        self.digits_width = pd_lines[3]
        self.limits = Bounds(lower=pd_lines[4], upper=pd_lines[5])
        self.flag = pd_lines[6] if 6 < len(pd_lines) else None
        if 7 < len(pd_lines):
          self.label = self.__d__.label if pd_lines[7] is None else pd_lines[7]
          self.comm = Comm(send=pd_lines[8], receive=pd_lines[9], default=self.__d__.receive)
        if 10 < len(pd_lines):
          self.font_size = self.__num__(pd_lines[10])
    
    if self.__cls__ == 'obj':
      self.__cls__ = self.className

  def __pd__(self):
    """ Returns the pd-code representation of the object """
    
    s = str(int(getattr(self,'digits_width',self.__d__.digits_width)))
    
    if not hasattr(self, "limits"):
      self.limits = Bounds(lower=self.__d__.limits['lower'], upper=self.__d__.limits['upper'])
    
    s += ' ' + self.limits.__pd__()
    s += " " + str(int(getattr(self,'flag', self.__d__.flag)))
    s += " " + str(getattr(self,'label',self.__d__.label))

    comm = getattr(self, 'comm', Comm(default=self.__d__.receive))
    s += " " + comm.__pd__(order=-1)
    if hasattr(self, 'font_size'):
      s += " " + str(self.font_size)
    
    return super().__pd__(s)
  
  def __xml__(self):
    """ Returns an XML Element for this object """
    return super().__xml__(scope=self, tag=self.className, attrib=('className','digits_width', 'limits', 'flag', 'label', 'comm', 'font_size'))