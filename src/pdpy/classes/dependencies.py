#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

from .base import Base

__all__ = ['Dependencies']

class Dependencies(Base):
  def __init__(self, *argv, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(cls='declare')
    if json is not None:
      super().__populate__(self, json)
    elif xml is not None:
      pass
    else:
      # python magic to split a list in pairs
      deps = list(zip(*[iter(argv)]*2))
      for dep in deps:
        if "-path" == dep[0]:
          self.updatePath(dep[1])
        elif "-lib" == dep[0]:
          self.updateLib(dep[1])
  
  def updatePath(self, path):
    if not hasattr(self, "paths"):
      self.paths = []
    self.paths.append(path)
  
  def updateLib(self, lib):
    if not hasattr(self, "libs"):
      self.libs = []
    self.libs.append(lib)
  
  def update(self, deps):
    if hasattr(deps, "paths"):
      if len(deps.paths):
        for path in deps.paths:
          self.updatePath(path)
    if hasattr(deps, "libs"):
      if len(deps.libs):
        for lib in deps.libs:
          self.updateLib(lib)

  def __pd__(self):
    """ Parses the dependencies into paths and libs """
    s = ''
    for x in getattr(self, 'paths', []):
      s += f" -path {x}"
    for x in getattr(self, 'libs', []):
      s += f" -lib {x}"
    return super().__pd__(s)

  def __xml__(self):
    """ Returns an XML Element for this object """
    x = super().__element__(self)
    for path in getattr(self, 'paths', []):
      super().__subelement__(x, 'path', text=path)
    for lib in getattr(self, 'libs', []):
      super().__subelement__(x, 'lib', text=lib)
    return x
