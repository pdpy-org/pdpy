#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Scalar Class Definition """

from . import data
from ..core.base import Base
from ..utilities.utils import log

__all__ = [ 'Scalar' ]

class Scalar(Base):
  def __init__(self, 
               struct=None,
               pd_lines=None,
               json=None,
               xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(cls='scalar')
    self.className = self.__cls__
    
    if json is not None:
      super().__populate__(self, json)
    
    elif xml is not None:
      self.name = xml.findtext('name')
      if xml.find('data'):
        self.data = data.Data(xml=xml.find('data'))
    
    elif pd_lines is not None:
      # log(1, 'Loading Scalar from Pd Lines:', pd_lines)
      self.name = pd_lines[0]
      for s in struct:
        if self.name == s.name:
          setattr(self, 'data', data.Data(data = pd_lines[1:], template = s))

  def __pd__(self):
    """ Returns the data of this scalar as a pd string """
    if hasattr(self, 'data'):
      root = super().__getroot__(self)
      # if hasattr(root, 'structs'):
      _, template = root.getTemplate(self.name)
      s = ''
      if hasattr(self.data, '__pd__'):
        s = self.data.__pd__(template)
      else:
        if self.data.__pdpy__ == 'List':
          s += ' ' + self.data.__pd__(template)
        else:
          s += ' ' + self.data.__pd__()
        s += self.__semi__
      return super().__pd__(self.name + ' ' + s)
      # else:
        # log(1, "Scalar Define")
        # s = "#X obj scalar define"
        # if hasattr(self, 'data'):
        #   s += ' -k'
        # if hasattr(self, 'name'):
        #   s += " " + str(self.name)"
        # s += self.__end__
        # if hasattr(self, 'data'):
        #   s += self.data.__pd__()
        # return s 
    else:
      return super().__pd__(self.name if hasattr(self, 'name') else '')

  def __xml__(self):
    """ Returns the XML Element for this objcet """
    x = super().__element__(scope=self, attrib={'pdpy':self.__pdpy__})
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