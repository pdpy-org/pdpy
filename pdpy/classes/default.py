#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
"""
Pure Data Default Values
========================
"""

__all__ = [
  'Namespace',
  'Default',
  'GOPArrayFlags',
  'IEMGuiNames',
  'PdNativeGuiNames',
  'PdFonts',
  'Formats',
  'getFormat'
]

class Namespace:
  """ PdPy Namespace """
  def __init__(self):
    import pdpy
    self.__module__ = pdpy
    self.__name__ = { 
      e.lower().replace('__', '') : e for e in dir(self.__module__) 
    }

  def __get__(self, name=None, tag=None):
    """ Get a PdPy Namespace Element """
    if name is not None:
      if name in self.__name__:
        name = self.__name__[name]
      elif name in self.__name__.values():
        name = name
      else:
        return name
      return getattr(self.__module__, name)
    
    elif tag is not None:
      # recurse with the tag
      return self.__get__(name=tag)

  def __check__(self, tag, attrib, attr_key='pdpy'):
    __pdpy__ = self.__get__(name=getattr(attrib, attr_key, None), tag=tag)
    if __pdpy__ is None:
      raise KeyError("No PdPy class found for element: " + str(tag))
    return __pdpy__


Formats = {
  "pkl" : [ "pickle", "pkl"],
  "json": [ "json" ],
  "pdpy" : [ "pdpy" ],
  "pd"  : [ "pd", "puredata"],
  "xml"  : [ "xml" ],
}

def getFormat(fmt):
  for k,v in Formats.items():
    for f in v:
      if fmt == f:
        return k
  return None




class Default(object):
  def __init__(self):
    self.screen       = { 'x':0, 'y': 22 }
    self.dimension    = { 'width': 450, 'height': 300 }
    self.arrdimen     = { 'width': 450, 'height': 278 }
    self.font         = { 'size': 12, 'face': 0 }
    self.array        = { 'size': 100, 'type': 'float', 'flag': 3}
    self.vis          = 0
    self.digits_width = { 'floatatom': 5, 'symbolatom': 10, 'listbox': 20 } 
    self.limits       = { 'lower':0, 'upper':0 } 
    self.flag         = 0
    self.label        = '-'
    self.receive      = '-'
    self.send         = '-'
    self.name         = '(subpatch)'
    self.iemgui = {
      'label'    : 'empty',
      'fontface' : 0,
      'fontsize' : 10,
      'fgcolor'  : '#000000'
    }
    self.iemgui.update({
      'vu': {
        'xoff':-1,
        'width':15,
        'height':120,
        'yoff':-8,
        'fsize':self.iemgui['fontsize'],
        'bgcolor':-66577,
        'lbcolor':-1,
        'scale':True,
        'flag':0
      },
      'tgl': {
        'size':15,
        'init':0,
        'xoff':17,
        'yoff':7,
        'fsize':self.iemgui['fontsize'],
        'bgcolor':'#fcfcfc',
        'lbcolor':'#000000',
        'flag':1,
        'nonzero':1
      },
      'cnv': {
        'size':15,
        'width':100,
        'height':60,
        'xoff':20,
        'yoff':12,
        'fsize':self.iemgui['fontsize'] + 4,
        'bgcolor':-66577,
        'lbcolor':-233017,
        'flag':1
      },
      'radio': {
        'size':15,
        'flag':1,
        'init':0,
        'number':8,
        'xoff':0,
        'yoff':-8,
        'fsize':self.iemgui['fontsize'],
        'bgcolor':'#fcfcfc',
        'lbcolor':'#000000',
        'value':0
      },
      'bng': {
        'size':15,
        'hold':250,
        'intrrpt':50,
        'init':0,
        'xoff':17,
        'yoff':7,
        'fsize':self.iemgui['fontsize'],
        'bgcolor':'#fcfcfc',
        'lbcolor':'#000000'
      },
      'nbx': {
        'digits_width':5,
        'height':14,
        'lower':0,
        'upper':0,
        'log_flag':0,
        'init':0,
        'xoff':0,
        'yoff':-8,
        'fsize':self.iemgui['fontsize'],
        'bgcolor':'#fcfcfc',
        'lbcolor':'#000000',
        'value':0,
        'log_height':256
      },
      'hsl': {
        'width':128,
        'height':15,
        'lower':0,
        'upper':127,
        'log_flag':0,
        'init':0,
        'xoff':-2,
        'yoff':-8,
        'fsize':self.iemgui['fontsize'],
        'bgcolor':'#fcfcfc',
        'lbcolor':'#000000',
        'log_height':256,
        'value':0,
        'steady':0
      },
      'vsl': {
        'width':15,
        'height':128,
        'lower':0,
        'upper':127,
        'log_flag':0,
        'init':0,
        'xoff':-2,
        'yoff':-8,
        'fsize':self.iemgui['fontsize'],
        'bgcolor':'#fcfcfc',
        'lbcolor':'#000000',
        'log_height':256,
        'value':0,
        'steady':0
      }
    }) # iemgui update
    self.xml = {
      'data_as_text': False
    }

GOPArrayFlags = [
  "polygon", "polygon-saved",
  "points", "points-saved",
  "bezier", "bezier-saved",
]
IEMGuiNames = [
  "hsl",
  "vsl",
  "cnv",
  "nbx",
  "hradio",
  "vradio",
  "vu",
  "tgl",
  "bng"
]
PdFonts = [
  "Menlo",
  "Helvetica",
  "Times"
]
PdNativeGuiNames = [
  'floatatom',
  'symbolatom',
  'listbox'
]