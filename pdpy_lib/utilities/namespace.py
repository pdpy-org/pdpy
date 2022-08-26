#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021-22 Fede Camara Halac
# **************************************************************************** #
"""
PdPy Namespace
==============
"""

__all__ = [ 'Namespace' ]

class Namespace:
  """ PdPy Namespace """
  def __init__(self):
    import pdpy_lib as pdpy
    self.__module__ = pdpy
    self.__name__ = { 
      e.lower().replace('__', '') : e for e in dir(self.__module__) 
    }
    # for i in self.__name__: print(i)

  def __get__(self, name=None, tag=None):
    """ Get a PdPy Namespace Element """
    print("get", name, tag)
    if name is not None:
      if name in self.__name__:
        name = self.__name__[name]
      elif name in self.__name__.values():
        name = name
      else:
        print("returning name:", name)
        return name
      print("returning attribute", getattr(self.__module__, name))
      return getattr(self.__module__, name)
    
    elif tag is not None:
      # recurse with the tag
      return self.__get__(name=tag)

  def __check__(self, tag, attrib, attr_key='pdpy'):
    __pdpy__ = self.__get__(name=getattr(attrib, attr_key, None), tag=tag)
    if __pdpy__ is None:
      raise KeyError("No PdPy class found for element: " + str(tag))
    return __pdpy__
