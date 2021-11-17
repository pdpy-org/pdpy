#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Canvas Class Definition """

from .base import Base
from ..util.utils import splitByEscapedChar

class PdData(Base):
  """ A PdData base class """
  def __init__(self, data=None, dtype=float, char=None, head=None):
    self.__pdpy__ = self.__class__.__name__
    self.dtype = dtype
    self.char = char
    if head is not None:
      self.head = head
    if self.char is not None:
      self.data = splitByEscapedChar(data, char=self.char)
    else:
      self.data = [self.dtype(d) for d in data]
  