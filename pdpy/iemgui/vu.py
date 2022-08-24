#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
"""
IEMGui Vu Meter
===============
"""

from ..objects.obj import Obj
from ..primitives.size import Size
from . import iemlabel

__all__ = [ 'Vu' ]

class Vu(Obj):
  """ The IEM Vu Meter Object, aka. ``vu``.

  This IEM gui object represents an IEM Vu Meter.
  
  Parameters
  ----------

  pd_lines : :class:`list`
    The lines of the Pure Data patch that define the object.
  
  json : :class:`dict`
    A JSON representation of the object.
  
  **kwargs: optional
    Keyword arguments are:

    *  ``width``: the width of the vu meter area
    *  ``height``: the height of the vu meter area
    *  ``scale``: flag to draw the dB scale or not
    *  ``flag``: another flag.
    *  ``bgcolor``: the background color of the vu meter
    *  ``fgcolor``: the foreground of the vu meter

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
      self.area = Size(*pd_lines[:2])
      self.comm = Comm(send=False, receive=pd_lines[2])
      self.label = iemlabel.IEMLabel(pd_lines = pd_lines[3:8] + [pd_lines[9]])
      self.bgcolor = self.__num__(pd_lines[8])
      self.scale= self.__pdbool__(pd_lines[10]) if 10 < len(pd_lines) else None
      self.flag = self.__pdbool__(pd_lines[11]) if 11 < len(pd_lines) else None
    
    elif json is not None:
      super().__init__(json=json)
    
    else:
      super().__init__(className='vu')
  
      iemgui = self.__d__.iemgui
      default = iemgui[self.className]

      super().__set_default__(kwargs, [
        ('area', default, lambda d: Size(w = d['width'], h = d['height'])),
        ('bgcolor', default, lambda x: self.__num__(x)),
        ('fgcolor', iemgui, lambda x: self.__num__(x)),
        ('scale', default, lambda x: self.__pdbool__(x)),
        ('flag', default, lambda x: self.__pdbool__(x)),
      ])

      self.comm = Comm(**kwargs)
      self.label = iemlabel.IEMLabel(className = self.className, **kwargs)

  def __pd__(self):
    """ Return the pd string for this object """
    s = self.area.__pd__()
    s +=  " " + str(self.comm.__pd__())
    s +=  " " + str(self.label.__pd__())
    s +=  " " + str(self.bgcolor)
    s +=  " " + str(self.label.lbcolor)
    if hasattr(self, 'scale') and self.scale is not None:
      s +=  " " + str(1 if self.scale else 0)
    if hasattr(self, 'flag') and self.flag is not None:
      s +=  " " + str(1 if self.flag else 0)
    return super().__pd__(s)
  
  def __xml__(self):
    """ Returns an XML Element for this object """
    return super().__xml__(scope=self, tag=self.__cls__, attrib=('area', 'comm', 'label', 'bgcolor', 'scale', 'flag'))
