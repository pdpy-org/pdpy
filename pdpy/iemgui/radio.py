#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021-22 Fede Camara Halac
# **************************************************************************** #
"""
IEMGui Radio
============
"""

from ..objects.obj import Obj
from ..primitives.size import Size
from . import iemlabel

__all__ = [ 'Radio' ]

class Radio(Obj):
  """ The IEM Radio object, aka. `hradio` or `vradio`
  
  This IEM gui object represents an IEM horizontal or vertical radio selector.
  
  Parameters
  ----------

  pd_lines : :class:`list`
    The lines of the Pure Data patch that define the object.
  
  json : :class:`dict`
    A JSON representation of the object.
  
  **kwargs: optional
    Keyword arguments are:

    *  ``size``: the size of each radio button
    *  ``flag``: a flag
    *  ``init``: the init flag to trigger the radio on loadtime
    *  ``number``: the number of buttons
    *  ``value``: the initial value of the radio button (with `init`)
    *  ``bgcolor``: the background color of the radio
    *  ``fgcolor``: the foreground of the radio

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
      self.size   = Size(pd_lines[0])
      self.flag   = self.__num__(pd_lines[1])
      self.init   = self.__pdbool__(pd_lines[2])
      self.number = self.__num__(pd_lines[3])
      self.comm = Comm(send=pd_lines[4], receive=pd_lines[5])
      self.label = iemlabel.IEMLabel(pd_lines = pd_lines[6:11] + [pd_lines[13]])
      self.bgcolor = self.__num__(pd_lines[11])
      self.fgcolor = self.__num__(pd_lines[12])
      self.value   = self.__num__(pd_lines[14])
    
    elif json is not None:
      super().__init__(json=json)
    
    else:

      if 'className' in kwargs:
        _c = kwargs.pop('className')
      else:
        _c = 'hradio' # just default to horizontal radio
      super().__init__(className=_c)
      
      iemgui = self.__d__.iemgui
      _cls = 'radio'
      default = iemgui[_cls]

      super().__set_default__(kwargs, [
        ('size', default, lambda x: Size(h = x)),
        ('flag', default, lambda x: self.__pdbool__(x)),
        ('init', default, lambda x: self.__pdbool__(x)),
        ('number', default, lambda x: self.__num__(x)),
        ('bgcolor', default, lambda x: self.__num__(x)),
        ('fgcolor', iemgui, lambda x: self.__num__(x)),
        ('value', default, lambda x: float(x)),
      ])

      self.comm = Comm(**kwargs)
      self.label = iemlabel.IEMLabel(className = _cls, **kwargs)
  
  def __pd__(self):
    """ Return the pd string for this object """
    s = self.size.__pd__()
    s += " " + str(1 if self.flag else 0)
    s += " " + str(1 if self.init is False else 0)
    s += " " + str(self.number)
    s += " " + str(self.comm.__pd__())
    s += " " + str(self.label.__pd__())
    s += " " + str(self.bgcolor)
    s += " " + str(self.fgcolor)
    s += " " + str(self.label.lbcolor)
    s += " " + str(self.value)
    return super().__pd__(s)

  def __xml__(self):
    """ Return the XML Element for this object """
    return super().__xml__(scope=self, tag=self.__cls__, attrib=('size', 'flag', 'init', 'number', 'comm', 'label', 'bgcolor', 'fgcolor', 'value'))
    
