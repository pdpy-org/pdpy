#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" IEMGUI Toggle Class Definitions """

from .classes import Size
from .connections import Comm
from .object import Object
from .iemgui import IEMLabel

__all__ = [ 'Toggle' ]

class Toggle(Object):
  """
  The IEM Toggle Object
  ======================

  The case of `tgl`
  --------------------
  
  The IEM gui object is a Toggle button.

  1. 5: `size`: the size of the toggle square
  2. 6: `init`: the init flag to trigger the toggle on loadtime
  3. 7: `send`: the sender symbol of the toggle
  3. 8: `receive`: the receiver symbol of the toggle
  4. 9-14: `IEMLabel` Parameters
  5. 15: `flag`: a flag
  6. 16: `nonzero`: the non-zero value when toggle is on.
  """

  def __init__(self, pd_lines=None, json=None):
    self.__pdpy__ = self.__class__.__name__
    if pd_lines is not None:
      super().__init__(pd_lines=pd_lines[:4])
      pd_lines = pd_lines[4:]
      self.size = Size(pd_lines[0])
      self.init = self.__pdbool__(pd_lines[1])
      self.comm = Comm(send=pd_lines[2], receive=pd_lines[3])
      self.label = IEMLabel(*pd_lines[4:9], pd_lines[11])
      self.bgcolor = self.__num__(pd_lines[9])
      self.fgcolor = self.__num__(pd_lines[10])
      self.flag    = self.__num__(pd_lines[12])
      self.nonzero = self.__num__(pd_lines[13])
    elif json is not None:
      super().__init__(json=json)

  def __pd__(self):
    """ Return the pd string for this object """
    s = self.size.__pd__()
    s += f" {1 if self.init is False else 0}"
    s += f" {self.comm.__pd__()}"
    s += f" {self.label.__pd__()}"
    s += f" {self.bgcolor}"
    s += f" {self.label.lbcolor}"
    s += f" {self.fgcolor}"
    s += f" {1 if self.flag else 0}"
    s += f" {self.nonzero}"
    return super().__pd__(s)

  def __xml__(self):
    """ Return the XML Element for this object """
    return super().__xml__(scope=self, attrib=('size', 'init', 'comm', 'label', 'bgcolor', 'fgcolor', 'flag', 'nonzero'))

