#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" IEMGUI Class Definitions """

from .base import Base
from .classes import Point
from .default import PdFonts

__all__ = [ 
  'IEMLabel',
  'IEMFont',
]

class IEMFont(Base):
  def __init__(self, face=None, points=None, json=None, xml=None):
    """ Initialize the object """
    self.__pdpy__ = self.__class__.__name__
    super().__init__(json=json, xml=xml)
    if json is None and xml is None:
      self.__pdpy__ = self.__class__.__name__
      self.face = self.__num__(face)
      self.name = PdFonts[self.face if self.face < len(PdFonts) else -1]
      self.points = self.__num__(points)
  
  def __pd__(self):
    """ Return the pd lines for this object """
    return f"{self.face} {self.points}"

  def __xml__(self, tag=None):
    """ Return the XML Element for this object """
    return super().__xml__(scope=self, tag=tag, attrib=('face', 'points'))

class IEMLabel(Base):
  """ 
  The IEM IEMLabel Object
  ====================

  Description
  -----------
  This is the base class for the IEM gui.

  Initialization Arguments
  ------------------------
  1. `label`: the label text
  2. `x`: the x-offset of the label
  3. `y`: the y-offset of the label
  4. `fface`: the font face of the label
  5. `fsize`: the font size of the label
  6. `lbcolor`: the color of the label
  """
  def __init__(self,
              label=None,
              xoff=None,
              yoff=None,
              fface=None,
              fsize=None,
              lbcolor=None,
              json=None,
              xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(json=json, xml=xml)
    if json is None and xml is None:
      self.__pdpy__ = self.__class__.__name__
      self.label = label if label is not None else self.__d__.iemgui['symbol']
      self.offset = Point(xoff, yoff)
      self.font = IEMFont(fface, fsize)
      self.lbcolor = self.__num__(lbcolor)

  def __pd__(self):
    """ Return the pd string for this iem label """
    return f"{self.label} {self.offset.__pd__()} {self.font.__pd__()}"

  def __xml__(self, tag=None):
    """ Return the XML Element for this iem label """
    return super().__xml__(scope=self, tag=tag, attrib=('label', 'offset', 'font', 'lbcolor'))
