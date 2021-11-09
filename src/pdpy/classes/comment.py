#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

from .base import Base
from .classes import Point
from ..util.utils import splitSemi

__all__ = [ 'Comment' ]

class Comment(Base):
  def __init__(self, *argv, x=None, y=None, json_dict=None, xml_object=None):
    self.__pdpy__ = self.__class__.__name__
    if isinstance(json_dict, dict):
      self.position = Point(json_dict=json_dict['position'])
      self.text = json_dict.get('text', None)
    elif xml_object is not None:
      self.position = Point(xml_object=xml_object.find('position'))
      self.text = x.text
    elif x is not None and y is not None:
      self.position = Point(x=x, y=y)
      # can have "\\,"
      # split at "\\;" 
      # and the unescaped comma is a border flag: ", f 80"
      argc = len(argv)
      argv = list(argv)
      if argc:
        if 2 < len(argv) and "f" == argv[-2] and argv[-1].isnumeric():
          self.border = self.num(argv[-1])
          argv = argv[:-2]
          argv[-1] = argv[-1].replace(",","")
        self.text = splitSemi(argv)
