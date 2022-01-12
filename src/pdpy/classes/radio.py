#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" IEMGUI Radio Class Definitions """

from .object import Object
from .size import Size
from .connections import Comm
from .iemgui import IEMLabel

__all__ = [ 'Radio' ]

class Radio(Object):
  """
  The IEM Radio Object
  =====================
  The case of `hradio` or `vradio`
  --------------------
  
  The IEM gui object is a IEM horizontal or vertica radio button.

  1. 5: `size`: the size of each radio button
  2. 6: `flag`: a flag
  2. 7: `init`: the init flag to trigger the radio on loadtime
  2. 8: `number`: the number of buttons
  3. 9: `send`: the sender symbol of the radio
  3. 10: `receive`: the receiver symbol of the radio
  4. 11-16: `IEMLabel` Parameters
  5. 17: `value`: the initial value of the radio button (with `init`)
  """

  def __init__(self, pd_lines=None, json=None):
    self.__pdpy__ = self.__class__.__name__
    if pd_lines is not None:
      super().__init__(pd_lines=pd_lines[:4])
      pd_lines = pd_lines[4:]
      self.size   = Size(pd_lines[0])
      self.flag   = self.__num__(pd_lines[1])
      self.init   = self.__pdbool__(pd_lines[2])
      self.number = self.__num__(pd_lines[3])
      self.comm = Comm(send=pd_lines[4], receive=pd_lines[5])
      self.label = IEMLabel(*pd_lines[6:11], pd_lines[13])
      self.bgcolor = self.__num__(pd_lines[11])
      self.fgcolor = self.__num__(pd_lines[12])
      self.value   = self.__num__(pd_lines[14])
    elif json is not None:
      super().__init__(json=json)
  
  def __pd__(self):
    """ Return the pd string for this object """
    s = self.size.__pd__()
    s += f" {1 if self.flag else 0}"
    s += f" {1 if self.init is False else 0}"
    s += f" {self.number}"
    s += f" {self.comm.__pd__()}"
    s += f" {self.label.__pd__()}"
    s += f" {self.bgcolor}"
    s += f" {self.fgcolor}"
    s += f" {self.label.lbcolor}"
    s += f" {self.value}"
    return super().__pd__(s)

  def __xml__(self):
    """ Return the XML Element for this object """
    return super().__xml__(scope=self, attrib=('size', 'flag', 'init', 'number', 'comm', 'label', 'bgcolor', 'fgcolor', 'value'))
    
