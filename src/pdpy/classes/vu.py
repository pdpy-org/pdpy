#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" IEMGUI Vu Meter Class Definitions """

from .classes import Size
from .connections import Comm
from .object import Object
from .iemgui import IEMLabel

__all__ = [ 'Vu' ]

class Vu(Object):
  """ 
  The IEM Vu Object
  ==================

  The IEM gui object is a vu meter.

  1. 5: `width`: the width of the vu meter area
  2. 6: `height`: the height of the vu meter area
  3. 7: `receive`: the receiver symbol of the vu meter
  4. 8-13: `IEMLabel` Parameters
  5. 14: `scale`: flag to draw the dB scale or not
  6. 15: `flag`: another flag.
  """

  def __init__(self, pd_lines=None, json=None):
    self.__pdpy__ = self.__class__.__name__
    if pd_lines is not None:
      super().__init__(pd_lines=pd_lines[:4])
      pd_lines = pd_lines[4:]
      self.area = Size(*pd_lines[:2])
      self.comm = Comm(send=False, receive=pd_lines[2])
      self.label = IEMLabel(*pd_lines[3:8], pd_lines[9])
      self.bgcolor = self.__num__(pd_lines[8])
      self.scale= self.__pdbool__(pd_lines[10]) if 10 < len(pd_lines) else None
      self.flag = self.__pdbool__(pd_lines[11]) if 11 < len(pd_lines) else None
    elif json is not None:
      super().__init__(json=json)

  def __pd__(self):
    """ Return the pd string for this object """
    s = self.area.__pd__()
    s += f" {self.comm.__pd__()}"
    s += f" {self.label.__pd__()}"
    s += f" {self.bgcolor}"
    s += f" {self.label.lbcolor}"
    if hasattr(self, 'scale') and self.scale is not None:
      s += f" {1 if self.scale else 0}"
    if hasattr(self, 'flag') and self.flag is not None:
      s += f" {1 if self.flag else 0}"
    return super().__pd__(s)
  
  def __xml__(self):
    """ Returns an XML Element for this object """
    return super().__xml__(scope=self, attrib=('area', 'comm', 'label', 'bgcolor', 'scale', 'flag'))
