#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Pure Data Text Comment Definitions """

from .base import Base
from .classes import Point
from ..util.utils import splitSemi

__all__ = [ 'Comment' ]

class Comment(Base):
  def __init__(self, pd_lines=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(cls='text')
    
    if json is not None:
      super().__populate__(self, json)
    elif xml is not None:
      self.position = Point(xml=xml.find('position'))
      self.text = xml.text
    elif pd_lines is not None:
      self.position = Point(x=pd_lines[0], y=pd_lines[1])
      # can have "\\,"
      # split at "\\;" 
      # and the unescaped comma is a border flag: ", f 80"
      argv = pd_lines[2:]
      if len(argv):
        if 2 < len(argv) and "f" == argv[-2] and argv[-1].isnumeric():
          self.border = self.__num__(argv[-1])
          argv = argv[:-2]
          argv[-1] = argv[-1].replace(",","")
        self.text = splitSemi(argv)

  def __pd__(self):
    """ Return a pd representation string """

    s = self.position.__pd__()

    if hasattr(self, 'text') and len(self.text):
      if len(self.text) == 1:
        s += f" {self.text[0]}"
      else:
        s += ' ' + ' '.join(list(map(lambda x:f"{x} \\;",list(self.text[:-1]))))
        s += f" {self.text[-1]}"

    if hasattr(self, "border"):
      s += f", f {self.border}"

    return super().__pd__(s)

  def __xml__(self):
    """ Return an xml representation object """
    return super().__xml__(scope=self, attrib=('text','position','border'))

  