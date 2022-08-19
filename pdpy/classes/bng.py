#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021-22 Fede Camara Halac
# **************************************************************************** #
""" 
IEMGui Bang
===========
"""

from .obj import Obj
from .size import Size
from .connections import Comm
from .iemgui import IEMLabel

__all__ = [ 'Bng' ]

class Bng(Obj):
  """ The IEM Bang Button Obj
  
  The IEM gui object is a IEM Bang button.

  * ``size``: the size of the button
  * ``hold``: time of the button on hold
  * ``intrrpt``: the interruption time of the button
  * ``init``: the init flag to trigger the button on loadtime
  * ``send``: the sender symbol of the button
  * ``receive``: the receiver symbol of the button
  * ``IEMLabel``: See :class:`pdpy.classes.iemgui.IEMLabel`

  Parameters
  ----------

  pd_lines : :class:`str`
    The lines of the Pure Data patch that define the object.
  
  json : :class:`dict`
    A JSON representation of the object.

  """

  def __init__(self, pd_lines=None, json=None, **kwargs):
    """ Constructor """

    self.__pdpy__ = self.__class__.__name__
    
    if pd_lines is not None:
      super().__init__(pd_lines=pd_lines[:4])
      pd_lines = pd_lines[4:]
      # log(1, "bng pd_lines: {}".format(pd_lines))
      self.size   = Size(pd_lines[0])
      self.hold   = self.__num__(pd_lines[1])
      self.intrrpt= self.__num__(pd_lines[2])
      self.init   = self.__pdbool__(pd_lines[3])
      self.comm = Comm(send=pd_lines[4], receive=pd_lines[5])
      self.label = IEMLabel(*pd_lines[6:11], pd_lines[13])
      self.bgcolor = self.__num__(pd_lines[11])
      self.fgcolor = self.__num__(pd_lines[12])
    
    elif json is not None:
      super().__init__(json=json)
    
    else:
      super().__init__(className='bng')
      if 'size' in kwargs:
        self.size = Size(w=kwargs.pop('size'))
      else:
        self.size = Size(w=self.__d__.iemgui['bng']['size'])
      self.hold = self.__d__.iemgui['bng']['hold']
      self.intrrpt= self.__d__.iemgui['bng']['intrrpt']
      self.init = self.__d__.iemgui['bng']['init']
      self.comm = Comm(
        send=self.__d__.iemgui['symbol'], 
        receive=self.__d__.iemgui['symbol'])
      self.label = IEMLabel(
        xoff=self.__d__.iemgui['bng']['xoff'],
        yoff=self.__d__.iemgui['bng']['yoff'],
        fface=self.__d__.iemgui['fontface'],
        fsize=self.__d__.iemgui['bng']['fsize'],
        lbcolor=self.__d__.iemgui['bng']['lbcolor'], **kwargs)
      self.bgcolor = self.__d__.iemgui['bng']['bgcolor']
      self.fgcolor = self.__d__.iemgui['fgcolor']

  def __pd__(self):
    """ Return the pd-lang string for this object """
    s = self.size.__pd__()
    s += " " + str(self.hold)
    s += " " + str(self.intrrpt)
    s += " " + str(1 if self.init is False else 0)
    s += " " + str(self.comm.__pd__())
    s += " " + str(self.label.__pd__())
    s += " " + str(self.bgcolor)
    s += " " + str(self.fgcolor)
    s += " " + str(self.label.lbcolor)
    return super().__pd__(s)

  def __xml__(self):
    """ Return the XML Element for this object """
    return super().__xml__(scope=self, tag=self.__cls__, attrib=('size', 'hold', 'intrrpt', 'init', 'comm', 'label', 'bgcolor', 'fgcolor'))

