#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" IEMGUI Number box Class Definitions """

from .obj import Obj
from .size import Size
from .bounds import Bounds
from .connections import Comm
from .iemgui import IEMLabel

__all__ = [ 'Nbx' ]

class Nbx(Obj):
  """
  The IEM Number Box Obj
  ==========================
  
  The IEM gui object is a IEM Number box (Number2).

  1. 5: `digits_width`: the width of the number box in digits.
  2. 6: `height`: the height of the numbers
  2. 7: `lower`: the lower limit of the number box range
  2. 8: `upper`: the upper limit of the number box range
  2. 9: `log_flag`: a flag to enable logarithmic value scaling
  2. 10: `init`: the init flag to trigger the number box on loadtime
  3. 11: `send`: the sender symbol of the number box
  3. 12: `receive`: the receiver symbol of the number box
  4. 13-18: `IEMLabel` Parameters
  5. 19: `value`: the initial value of the number box (with `init`)
  5. 20: `log_height`: upper limit of the log scale (with `log_flag`)
  """
  def __init__(self, pd_lines=None, json=None):
    self.__pdpy__ = self.__class__.__name__
    if pd_lines is not None:
      super().__init__(pd_lines=pd_lines[:4])
      pd_lines = pd_lines[4:]
      self.digit_width = self.__num__(pd_lines[0])
      self.size   = Size(h=pd_lines[1])
      self.limits = Bounds(*pd_lines[2:4])
      self.log_flag = self.__pdbool__(pd_lines[4])
      self.init    = self.__pdbool__(pd_lines[5])
      self.comm = Comm(send=pd_lines[6], receive=pd_lines[7])
      self.label = IEMLabel(*pd_lines[8:13], pd_lines[15])
      self.bgcolor = self.__num__(pd_lines[13])
      self.fgcolor = self.__num__(pd_lines[14])
      self.value = float(pd_lines[16])
      self.log_height = self.__num__(pd_lines[17])
    elif json is not None:
      super().__init__(json=json)
  
  def __pd__(self):
    """ Return the pd string for this object """
    s = str(self.digit_width)
    s += f" {self.size.__pd__()}"
    s += f" {self.limits.__pd__()}"
    s += f" {1 if self.log_flag else 0}"
    s += f" {1 if self.init is False else 0}"    
    s += f" {self.comm.__pd__()}"
    s += f" {self.label.__pd__()}"
    s += f" {self.bgcolor}"
    s += f" {self.fgcolor}"
    s += f" {self.label.lbcolor}"
    s += f" {self.value}"
    s += f" {self.log_height}"
    return super().__pd__(s)

  def __xml__(self):
    """ Return the XML Element for this object """
    return super().__xml__(scope=self, tag=self.__cls__, attrib=('digit_width', 'size', 'limits', 'log_flag', 'init', 'comm', 'label', 'bgcolor', 'fgcolor', 'value', 'log_height'))

