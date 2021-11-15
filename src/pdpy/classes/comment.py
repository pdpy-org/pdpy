#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

from .base import Base
from .classes import Point
from ..util.utils import splitSemi

__all__ = [ 'Comment' ]

class Comment(Base):
  def __init__(self, pd_lines=None, json_dict=None, xml_object=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(pdtype='X', cls='text')
    
    if json_dict is not None:
      super().__populate__(self, json_dict)
    elif xml_object is not None:
      self.position = Point(xml_object=xml_object.find('position'))
      self.text = xml_object.text
    elif pd_lines is not None:
      self.position = Point(x=pd_lines[0], y=pd_lines[1])
      # can have "\\,"
      # split at "\\;" 
      # and the unescaped comma is a border flag: ", f 80"
      argv = pd_lines[2:]
      if len(argv):
        if 2 < len(argv) and "f" == argv[-2] and argv[-1].isnumeric():
          self.border = self.num(argv[-1])
          argv = argv[:-2]
          argv[-1] = argv[-1].replace(",","")
        self.text = splitSemi(argv)

  def __pd__(self):
    """ Return a pd representation string """

    s = super().__pd__()
    s += ' ' + self.position.__pd__()

    if hasattr(self, 'text'):
      if len(self.text) == 1: 
        s += ' ' + self.text[0]
      else: 
        s += ' ' + ' '.join([ f"{txt} \\;" for txt in self.text ])
    
    # TODO: is this placing doubly escaped commas?
    s = s.replace(',',' \\,')
    
    s += f", f {self.border}" if hasattr(self, 'border') else ''

    return s + self.__end__


