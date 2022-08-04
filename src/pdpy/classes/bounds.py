#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
""" Graphical Bounds Class Definitions """

from .base import Base

__all__ = ['Bounds']

class Bounds(Base):
  def __init__(self,
               lower=None,
               upper=None,
               dtype=float,
               json=None,
               xml=None
               ):
    self.__pdpy__ = self.__class__.__name__
    super().__init__()
    if json is not None:
      super().__populate__(self, json)
    elif xml is not None:
      self.lower = dtype(xml.findtext('lower'))
      self.upper = dtype(xml.findtext('upper'))
    elif json is None and xml is None:
      self.lower = dtype(lower) if lower is not None else dtype(0)
      self.upper = dtype(upper) if upper is not None else dtype(0)

  def __pd__(self):
    return str(self.lower) + " " + str(self.upper)

  def __xml__(self, tag=None):
    """ Return an XML Element """
    return super().__xml__(scope=self, tag=tag, attrib=('lower', 'upper'))

