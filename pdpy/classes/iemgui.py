#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" 
IEMGUI Label and Font 
=====================
"""

from .base import Base
from .point import Point
from .default import PdFonts

__all__ = [ 
  'IEMLabel',
  'IEMFont',
]

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

class IEMLabel(Base):
  """ The IEM IEMLabel Obj

  This is the base class for all IEM gui.

  Parameters
  ----------
  
  label : :class:`str`
    the label text
    
  x : :class:`int`
    the x-offset of the label
    
  y : :class:`int`
    the y-offset of the label
    
  fface : :class:`int`
    the font face of the label
    
  fsize : :class:`int`
    the font size of the label
    
  lbcolor : :class:`str`
    the color of the label
    
  """
  def __init__(self, pd_lines=None, json=None, xml=None, **kwargs):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(json=json, xml=xml)
    if json is None and xml is None and pd_lines is None:
      self.__pdpy__ = self.__class__.__name__
      default = self.__d__
      iemgui = default.iemgui
      className = kwargs.pop('className')
      self.__set_default__(kwargs, [
        ('label', iemgui),
        ('offset', iemgui[className], lambda d:Point(d['xoff'],d['yoff'])),
        ('lbcolor', iemgui[className], lambda d:self.__num__(d))
      ])
      self.font = IEMFont(**kwargs)
    elif pd_lines is not None:
      self.label = pd_lines[0]
      self.offset = Point(pd_lines[1], pd_lines[2])
      self.font = IEMFont(face=pd_lines[3], points=pd_lines[4])
      self.lbcolor = self.__num__(pd_lines[5])

  def __pd__(self):
    """ Return the pd-lang string for this iem label """
    return str(self.label) + " " + self.offset.__pd__() + " " + self.font.__pd__()

  def __xml__(self, tag=None):
    """ Return the XML Element for this iem label """
    return super().__xml__(scope=self, tag=tag, attrib=('label', 'offset', 'font', 'lbcolor'))
