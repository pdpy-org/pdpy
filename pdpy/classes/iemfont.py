#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021-22 Fede Camara Halac
# **************************************************************************** #
""" 
IEMGui Font
===========
"""

from .base import Base
from .default import PdFonts

__all__ = [ 'IEMFont' ]

class IEMFont(Base):
  """ Represents the IEM gui fonts 
  
  """
  def __init__(self, face=None, points=None, json=None, xml=None, **kwargs):
    """ Initialize the object """
    
    self.__pdpy__ = self.__class__.__name__
    
    super().__init__(json=json, xml=xml)
    
    if json is None and xml is None:
      
      self.__pdpy__ = self.__class__.__name__
      
      if face is not None:
        self.face = self.__num__(face)
      else:
        self.face = self.__d__.iemgui['fontface']
      
      
      if points is not None:
        self.points = self.__num__(points)
      else:
        self.points = self.__d__.iemgui['fontsize']
      
      self.name = PdFonts[self.face if self.face < len(PdFonts) else -1]
  
  def __pd__(self):
    """ Return the pd lines for this object """
    return str(self.face) + " " + str(self.points)

  def __xml__(self, tag=None):
    """ Return the XML Element for this object """
    return super().__xml__(scope=self, tag=tag, attrib=('face', 'points'))
