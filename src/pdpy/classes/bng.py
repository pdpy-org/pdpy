#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" IEMGUI Bang Class Definitions """

from .object import Object
from .size import Size
from .connections import Comm
from .iemgui import IEMLabel

__all__ = [ 'Bng' ]

class Bng(Object):
  """
  The IEM Button Object
  =====================
  
  The IEM gui object is a IEM Bang button.

  1. 5: `size`: the size of the button
  2. 6: `hold`: time of the button on hold
  2. 7: `intrrpt`: the interruption time of the button
  2. 8: `init`: the init flag to trigger the button on loadtime
  3. 9: `send`: the sender symbol of the button
  3. 10: `receive`: the receiver symbol of the button
  4. 11-16: `IEMLabel` Parameters
  """

  def __init__(self, pd_lines=None, json=None):
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
  
  def __pd__(self):
    """ Return the pd string for this object """
    s = self.size.__pd__()
    s += f" {self.hold}"
    s += f" {self.intrrpt}"
    s += f" {1 if self.init is False else 0}"
    s += f" {self.comm.__pd__()}"
    s += f" {self.label.__pd__()}"
    s += f" {self.bgcolor}"
    s += f" {self.fgcolor}"
    s += f" {self.label.lbcolor}"
    return super().__pd__(s)

  def __xml__(self):
    """ Return the XML Element for this object """
    return super().__xml__(scope=self, attrib=('size', 'hold', 'intrrpt', 'init', 'comm', 'label', 'bgcolor', 'fgcolor'))

