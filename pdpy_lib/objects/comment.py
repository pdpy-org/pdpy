#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" 
Comment
=======
"""

from ..core.object import Object
from ..primitives.point import Point
from ..utilities.utils import splitSemi

__all__ = [ 'Comment' ]

class Comment(Object):
  """ A Pure Data comment """
  
  def __init__(self, comments=None, pd_lines=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(cls='text')
    
    if json is not None:
      super().__populate__(self, json)
    elif xml is not None:
      self.position = Point(xml=xml.find('position'))
      self.border = xml.findtext('border', None)
      if xml.find('text'):
        self.text = [x.text for x in xml.find('text').findall('txt')]
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
    elif comments is not None:
      if not isinstance(comments, list):
        comments = [comments]    
      for comment in comments:
        self.addtext(comment)
    else:
      self.position = Point()

  def __pd__(self):
    """ Return a pd representation string """

    s = ''

    if hasattr(self, 'text') and len(self.text):
      if len(self.text) == 1:
        s += " " + str(self.text[0])
      else:
        s += ' ' + ' '.join(list(map(lambda x:str(x)+ " \\;",list(self.text[:-1]))))
        s += " " + str(self.text[-1])

    if hasattr(self, "border"):
      s += ", f " + str(self.border)

    return super().__pd__(s)

  def __xml__(self):
    """ Return an xml representation object """
    x = super().__xml__(scope=self, attrib='border')
        
    if hasattr(self, 'text'):
      text = super().__element__(tag='text')
      for t in getattr(self, 'text', []):
        super().__subelement__(text, 'txt', text=t)
      super().__subelement__(x, text)

    return x
    
  def addtext(self, text):
    """ Add a text row to the comment. It will be semicolon-terminated. """
    if not hasattr(self, 'text'):
      self.text = []
    self.text.append(text.replace(',', ' \\,').replace(';', ' \\;'))
  