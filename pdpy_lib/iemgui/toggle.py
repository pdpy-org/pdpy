#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021-22 Fede Camara Halac
# **************************************************************************** #
"""
IEMGui Toggle
=============
"""

from ..objects.obj import Obj
from ..primitives.size import Size
from . import iemlabel

__all__ = [ 'Toggle' ]

class Toggle(Obj):
  """ The IEM Toggle Obj, aka. `tgl`
  
  This IEM gui object represents an IEM toggle.
  
  Parameters
  ----------

  pd_lines : :class:`list`
    The lines of the Pure Data patch that define the object.
  
  json : :class:`dict`
    A JSON representation of the object.
  
  **kwargs: optional
    Keyword arguments are:

    *  ``size``: the size of the toggle square
    *  ``init``: the init flag to trigger the toggle on loadtime
    *  ``flag``: a flag
    *  ``nonzero``: the non-zero value when toggle is on.
    *  ``bgcolor``: the background color of the toggle
    *  ``fgcolor``: the foreground of the toggle
  
    Other keyword arguments are passed to :class:`pdpy.IEMLabel` and :class:`pdpy.Comm`
  
  See also
  --------
  :class:`pdpy.utilities.default.Default`
    For default parameters.
  
  """
  def __init__(self, pd_lines=None, json=None, **kwargs):

    from ..patching.comm import Comm
        
    self.__pdpy__ = self.__class__.__name__
    
    if pd_lines is not None:
      super().__init__(pd_lines=pd_lines[:4])
      pd_lines = pd_lines[4:]
      self.size = Size(pd_lines[0])
      self.init = self.__pdbool__(pd_lines[1])
      self.comm = Comm(send=pd_lines[2], receive=pd_lines[3])
      self.label = iemlabel.IEMLabel(pd_lines = pd_lines[4:9] + [pd_lines[11]])
      self.bgcolor = self.__num__(pd_lines[9])
      self.fgcolor = self.__num__(pd_lines[10])
      self.flag    = self.__num__(pd_lines[12])
      self.nonzero = self.__num__(pd_lines[13])
    
    elif json is not None:
      super().__init__(json=json)
    
    else:

      super().__init__(className='tgl')
      
      iemgui = self.__d__.iemgui
      default = iemgui[self.className]
      
      super().__set_default__(kwargs, [
        ('size', default, lambda x: Size(w = x)),
        ('init', default, lambda x: self.__pdbool__(x)),
        ('bgcolor', default, lambda x: self.__num__(x)),
        ('fgcolor', iemgui, lambda x: self.__num__(x)),
        ('flag', default, lambda x: self.__num__(x)),
        ('nonzero', default, lambda x: self.__num__(x)),
      ])

      self.comm = Comm(**kwargs)
      self.label = iemlabel.IEMLabel(className = self.className, **kwargs)

  def __pd__(self):
    """ Return the pd string for this object """
    s = self.size.__pd__()
    s += " " + str(1 if self.init is False else 0)
    s += " " + str(self.comm.__pd__())
    s += " " + str(self.label.__pd__())
    s += " " + str(self.bgcolor)
    s += " " + str(self.label.lbcolor)
    s += " " + str(self.fgcolor)
    s += " " + str(1 if self.flag else 0)
    s += " " + str(self.nonzero)
    return super().__pd__(s)

  def __xml__(self):
    """ Return the XML Element for this object """
    return super().__xml__(scope=self, tag=self.__cls__, attrib=('size', 'init', 'comm', 'label', 'bgcolor', 'fgcolor', 'flag', 'nonzero'))

