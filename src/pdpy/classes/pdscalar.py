#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Scalar Class Definition """

from pdpy.util.utils import log
from .base import Base
from .pddata import PdData

__all__ = [ 'Scalar' ]

# TODO: so, what if we just fill the Struct with the scalar data
# instead of this Scalar class? maybe forget this class and use only Struct?
# Not really, though. Let's just use one Struct to define many scalars, 
# like pd does.

class Scalar(Base):
  def __init__(self, 
               struct=None,
               pd_lines=None,
               json=None,
               xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(cls='scalar')
    self.className = self.__cls__
    
    if pd_lines is not None:
      self.parsePd(struct, pd_lines)
    elif json is not None:
      super().__populate__(self, json)
    elif xml is not None:
      self.name = xml.findtext('name')
      if xml.find('data'):
        self.data = PdData(xml=xml.find('data'))

  def parsePd(self, struct, argv):
    self.name = argv[0]
    for s in struct:
      if self.name == s.name:
        setattr(self, 'data', PdData(data = argv[1:], template = s))
    
  def __pd__(self):
    """ Returns the data of this scalar as a pd string """
    if hasattr(self, 'data'):
      _, template = super().__getroot__(self).getTemplate(self.name)
      s = ''
      if hasattr(self.data, '__pd__'):
        s = self.data.__pd__(template)
      else:
        for d in getattr(self, 'data', []):
          if d.__pdpy__ == 'PdList':
            s += ' ' + d.__pd__(template)
          else:
            s += ' ' + d.__pd__()
        s += self.__semi__
      return super().__pd__(self.name + ' ' + s)
    else:
      return super().__pd__(self.name)

  def __xml__(self):
    """ Returns the XML Element for this objcet """
    x = super().__element__(self)
    super().__subelement__(x, 'name', text=self.name)
    if hasattr(self, 'data'):
      _, template = super().__getroot__(self).getTemplate(self.name)
      if hasattr(self.data, '__xml__'):
        super().__subelement__(x, self.data.__xml__(template))
      else:
        data = super().__element__(tag='data')
        for d in getattr(self, 'data', []):
          super().__subelement__(data, d.__xml__(template))
        super().__subelement__(x, data)

    return x