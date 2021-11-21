#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Pure Data Default Definitions """

__all__ = [
  'Default',
  'XmlTagConvert',
  'GOPArrayFlags',
  'IEMGuiNames',
  'PdNativeGuiNames',
  'PdFonts',
  'Formats',
  'getFormat'
]

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

  def to_tilde(self, tag):
    """ Returns the tag name replacing tilde char with _tilde """
    if '~' in tag:
      return tag.replace("~", "_tilde")
    else:
      return tag

  def from_tilde(self, tag):
    """ Returns the tag name replacing _tilde with tilde char """
    if '_tilde' in tag:
      return tag.replace("_tilde", "~")
    else:
      return tag

  def to_xml_tag(self, tag):
    """ Returns the tag name replacing special characters """
    _tag = self.to_tilde(tag)
    for key, value in self.table.items():
      if key in _tag:
        _tag = _tag.replace(key, value) 
    return _tag


  def to_pd_obj(self, pd_key):
    """ Returns the tag name replacing special characters """
    _tag = self.from_tilde(pd_key)
    for key, value in self.table.items():
      if key in _tag:
        _tag = _tag.replace(value, key) 
    return _tag

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