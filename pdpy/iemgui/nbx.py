#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021-22 Fede Camara Halac
# **************************************************************************** #
""" 
IEMGui Number Box
=================
"""

from ..objects.obj import Obj
from ..primitives.size import Size
from ..primitives.bounds import Bounds
from . import iemlabel

__all__ = [ 'Nbx' ]

class Nbx(Obj):
  """ The IEM Number Box object, aka. ``nbx``
  
  This IEM gui object represents an IEM Number box (Number2)
  
  Parameters
  ----------

  pd_lines : :class:`list`
    The lines of the Pure Data patch that define the object.
  
  json : :class:`dict`
    A JSON representation of the object.
  
  **kwargs: optional
    Keyword arguments are:
    
    * ``digits_width``: the width of the number box in digits.
    * ``height``: the height of the numbers
    * ``lower``: the lower limit of the number box range
    * ``upper``: the upper limit of the number box range
    * ``log_flag``: a flag to enable logarithmic value scaling
    * ``init``: the init flag to trigger the number box on loadtime
    * ``value``: the initial value of the number box (with ``init``)
    * ``log_height``: upper limit of the log scale (with ``log_flag``)
    * ``bgcolor``: the background color of the bang
    * ``fgcolor``: the foreground of the bang
    
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
      self.digits_width = self.__num__(pd_lines[0])
      self.size   = Size(h=pd_lines[1])
      self.limits = Bounds(*pd_lines[2:4])
      self.log_flag = self.__pdbool__(pd_lines[4])
      self.init    = self.__pdbool__(pd_lines[5])
      self.comm = Comm(send=pd_lines[6], receive=pd_lines[7])
      self.label = iemlabel.IEMLabel(pd_lines = pd_lines[8:13] + [pd_lines[15]])
      self.bgcolor = self.__num__(pd_lines[13])
      self.fgcolor = self.__num__(pd_lines[14])
      self.value = float(pd_lines[16])
      self.log_height = self.__num__(pd_lines[17])
    elif json is not None:
      super().__init__(json=json)
    else:
      super().__init__(className='nbx')
      
      iemgui = self.__d__.iemgui
      default = iemgui[self.className]

      super().__set_default__(kwargs, [
        ('digits_width', default, lambda x: self.__num__(x)),
        ('size', default, lambda x: Size(h = x['height'])),
        ('limits', default, lambda d: Bounds(lower = d['lower'], upper = d['upper'])),
        ('init', default, lambda x: self.__pdbool__(x)),
        ('log_flag', default, lambda x: self.__pdbool__(x)),
        ('bgcolor', default, lambda x: self.__num__(x)),
        ('fgcolor', iemgui, lambda x: self.__num__(x)),
        ('value', default, lambda x: float(x)),
        ('log_height', default, lambda x: self.__num__(x)),
      ])

      self.comm = Comm(**kwargs)
      self.label = iemlabel.IEMLabel(className = self.className, **kwargs)
  
  def __pd__(self):
    """ Return the pd string for this object """
    s = str(self.digits_width)
    s += " " + str(self.size.__pd__())
    s += " " + str(self.limits.__pd__())
    s += " " + str(1 if self.log_flag else 0)
    s += " " + str(1 if self.init is False else 0)
    s += " " + str(self.comm.__pd__())
    s += " " + str(self.label.__pd__())
    s += " " + str(self.bgcolor)
    s += " " + str(self.fgcolor)
    s += " " + str(self.label.lbcolor)
    s += " " + str(self.value)
    s += " " + str(self.log_height)
    return super().__pd__(s)

  def __xml__(self):
    """ Return the XML Element for this object """
    return super().__xml__(scope=self, tag=self.__cls__, attrib=('digits_width', 'size', 'limits', 'log_flag', 'init', 'comm', 'label', 'bgcolor', 'fgcolor', 'value', 'log_height'))

