#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Pure Data Default Definitions """

__all__ = [
  'Namespace',
  'Default',
  'XmlTagConvert',
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
    self.__name__ = { e.lower().replace('__', ''):e for e in dir(self.__module__) }

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
      raise KeyError(f"No PdPy class found for element: {tag}")
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



class XmlTagConvert(object):
  def __init__(self):    
    self.table = {
      '%'  : 'op_mod',
      '*'  : 'op_mul',
      '-'  : 'op_minus',
      '+'  : 'op_plus',
      '/'  : 'op_div',
      '==' : 'op_eq',
      '!=' : 'op_ne',
      '>'  : 'op_gt',
      '<'  : 'op_lt',
      '>=' : 'op_ge',
      '<=' : 'op_le',
      '||' : 'op_or',
      '&&' : 'op_and',
      '!'  : 'op_not',
      '&'  : 'binop_and',
      '|'  : 'binop_bor',
      '>>' : 'binop_ls',
      '<<' : 'binop_rs'
    }
    self.tilde = "~"
    self.__tilde__ = "_tilde"
  
  def find(self, element, string):
    result = element in string
    # print('find', element, string, result)
    return result

  def to_tilde(self, tag):
    """ Returns the tag name replacing tilde char with _tilde """
    
    if not self.find(self.tilde, tag):
      return tag
    s = str(tag).replace(self.tilde, self.__tilde__)
    # print(f"to_tilde(): {tag} --> {s}")
    return s

  def from_tilde(self, tag):
    """ Returns the tag name replacing _tilde with tilde char """
    if not self.find(self.__tilde__, tag):
      return tag
    s = str(tag).replace(self.__tilde__, self.tilde)
    # print(f"from_tilde(): {tag} --> {s}")
    return s

  def to_xml_tag(self, key):
    """ Returns the tag name replacing special characters """
    # print(f"to_xml_tag(): {key}")
    tag = key
    if self.find(self.tilde, key):
      key_notilde = str(key).replace(self.tilde, '')
      if key_notilde in self.table:
        tag = self.table[key_notilde]
      else:
        # print(f'to_xml_tag(): tilde {key} not in table:', key)
        pass
      tag = self.to_tilde(tag)
    else:
      if key in self.table:
        tag = self.table[key]
      else:
        for k, v in self.table.items():
          if k in key:
            tag = v
            break
        # print('to_xml_tag(): key not in table:', key)
        tag = key
    print(f"to_xml_tag(): {key} --> {tag}")
    # argh, we need to check again for internal characters, eg: <mul_*_tilde>
    for i,e in enumerate(tag):
      for k in self.table.keys():
        if e == k:
          tag = tag[:i] + self.table[k] + tag[i+1:]
          break
    return tag


  def to_pd_obj(self, pd_key):
    """ Returns the tag name replacing special characters """
    _tag = self.from_tilde(pd_key)
    for key, value in self.table.items():
      if key in _tag:
        _tag = _tag.replace(value, key) 
    return _tag
  
  def isvalid(self, tag):
    """ Returns True if the tag is valid """
    if self.find('.', tag):
      return False
    elif self.find('/', tag):
      return False
    elif self.find('\\', tag):
      return False
    else:
      return self.to_xml_tag(tag)

class Default(object):
  def __init__(self):
    self.screen       = { 'x':0, 'y': 22 }
    self.dimen        = { 'width': 450, 'height': 300 }
    self.font         = { 'size': 12, 'face': 0 }
    self.array        = { 'size': 100 }
    self.vis          = 0
    self.digits_width = 0 
    self.limits       = { 'lower':0, 'upper':0 } 
    self.flag         = 0
    self.label        = '-'
    self.receive      = '-'
    self.send         = '-'
    self.name         = '(subpatch)'
    self.iemgui = {
      'symbol'   : 'empty',
      'fontface' : 0,
      'fgcolor'  : -1,
      'vu': {
        'xoff':-1,
        'width':15,
        'height':120,
        'yoff':-8,
        'fsize':10,
        'bgcolor':-66577,
        'lbcolor':-1,
        'scale':True,
        'flag':1
      },
      'tgl': {
        'size':15,
        'init':0,
        'xoff':17,
        'yoff':7,
        'fsize':10,
        'bgcolor':-262144,
        'lbcolor':-1,
        'flag':1,
        'nonzero':1
      },
      'cnv': {
        'size':15,
        'width':100,
        'height':60,
        'xoff':20,
        'yoff':12,
        'fsize':14,
        'bgcolor':-233017,
        'lbcolor':-66577,
        'flag':1
      },
      'radio': {
        'size':15,
        'flag':1,
        'init':0,
        'number':8,
        'xoff':0,
        'yoff':-8,
        'fsize':10,
        'bgcolor':-262144,
        'lbcolor':-1,
        'value':0
      },
      'bng': {
        'size':15,
        'hold':250,
        'intrrpt':50,
        'init':0,
        'xoff':17,
        'yoff':7,
        'fsize':10,
        'bgcolor':-262144,
        'lbcolor':-1
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
        'fsize':10,
        'bgcolor':-262144,
        'lbcolor':-1,
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
        'fsize':10,
        'bgcolor':-262144,
        'lbcolor':-1,
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
        'fsize':10,
        'bgcolor':-262144,
        'lbcolor':-1,
        'log_height':256,
        'value':0,
        'steady':0
      }
    }
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