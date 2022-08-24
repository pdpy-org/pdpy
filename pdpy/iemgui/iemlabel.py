#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021-22 Fede Camara Halac
# **************************************************************************** #
""" 
IEMGui Label
============
"""

from ..core.base import Base
from ..primitives.point import Point
from . import iemfont

__all__ = [ 'IEMLabel' ]

class IEMLabel(Base):
  """ The IEM IEMLabel Obj

  This IEM gui object represents an IEM Label
  
  Parameters
  ----------
  
  pd_lines : :class:`list`
    The lines of the Pure Data patch that define the object.
  
  json : :class:`dict`
    A JSON representation of the object.

  xml : ``xml.etree.ElementTree.Element`` or ``None``
    An Xml Element with the appropriate element structure.  
  
  **kwargs: optional
    Keyword arguments are:
    
    * ``label``: (:class:`str`) the label text
    * ``x``: (:class:`int`) the x-offset of the label
    * ``y``: (:class:`int`) the y-offset of the label
    * ``fface``: (:class:`int`) the font face of the label
    * ``fsize``: (:class:`int`) the font size of the label  
    * ``lbcolor``: (:class:`str`) the color of the label
  
  See also
  --------
  :class:`pdpy.utilities.default.Default`
    For default parameters.
    
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
      self.font = iemfont.IEMFont(**kwargs)
    elif pd_lines is not None:
      self.label = pd_lines[0]
      self.offset = Point(pd_lines[1], pd_lines[2])
      self.font = iemfont.IEMFont(face=pd_lines[3], points=pd_lines[4])
      self.lbcolor = self.__num__(pd_lines[5])

  def __pd__(self):
    """ Return the pd-lang string for this iem label """
    return str(self.label) + " " + self.offset.__pd__() + " " + self.font.__pd__()

  def __xml__(self, tag=None):
    """ Return the XML Element for this iem label """
    return super().__xml__(scope=self, tag=tag, attrib=('label', 'offset', 'font', 'lbcolor'))
