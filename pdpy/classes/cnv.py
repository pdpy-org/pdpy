#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
"""
Cnv
===
"""

from .size import Size
from .connections import Comm
from .obj import Obj
from .iemgui import IEMLabel

__all__ = [ 'Cnv' ]

class Cnv(Obj):
  """ The IEM Canvas Obj: The case of `cnv` or `my_canvas`
    
  The IEM gui object is a IEM canvas.

  1. 5: `size`: the size of the canvas mouse selection box
  2. 6: `width`: the width of the canvas area
  2. 7: `height`: the height of the canvas area
  3. 8: `send`: the sender symbol of the canvas # why is this here?
  3. 9: `receive`: the receiver symbol of the toggle
  4. 10-15: `IEMLabel` Parameters
  5. 16: `flag`: a flag
  
  """
  def __init__(self, pd_lines=None, json=None, **kwargs):
    self.__pdpy__ = self.__class__.__name__
    if pd_lines is not None:
      super().__init__(pd_lines=pd_lines[:4])
      pd_lines = pd_lines[4:]
      self.size = Size(pd_lines[0])
      self.area = Size(*pd_lines[1:3])
      if 12 < len(pd_lines):
        self.comm = Comm(send=pd_lines[3], receive=pd_lines[4])
        off = 0
      else:
        self.comm = Comm(send=False,receive=pd_lines[3])
        off = 1
      self.label = IEMLabel(pd_lines=pd_lines[5-off:10-off]+[pd_lines[11-off]])
      self.bgcolor = self.__num__(pd_lines[10-off])
      self.flag    = self.__num__(pd_lines[12-off])
    elif json is not None:
      super().__init__(json=json)
    else:
      super().__init__(className='cnv')

      iemgui = self.__d__.iemgui
      default = iemgui[self.className]
      
      super().__set_default__(kwargs, [
        ('size', default, lambda x: Size(w = x)),
        ('area', default, lambda d: Size(w = d['width'], h = d['height'])),
        ('bgcolor', default, lambda x: self.__num__(x)),
        ('fgcolor', iemgui, lambda x: self.__num__(x)),
        ('flag', default, lambda x: self.__pdbool__(x)),
      ])

      self.comm = Comm(**kwargs)
      self.label = IEMLabel(className = self.className, **kwargs)

  def __pd__(self):
    """ Return the pd string for this object """
    s = self.size.__pd__()
    s += " " + self.area.__pd__()
    s += " " + self.comm.__pd__()
    s += " " + self.label.__pd__()
    s += " " + str(self.bgcolor)
    s += " " + str(self.label.lbcolor)
    s += " " + str(1 if self.flag else 0)
    return super().__pd__(s)

  def __xml__(self):
    """ Return the XML Element for this object """
    return super().__xml__(scope=self, tag=self.__cls__, attrib=('size', 'area', 'comm', 'label', 'bgcolor', 'flag'))

