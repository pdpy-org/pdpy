#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
"""
Pure Data Default Values
========================
"""

__all__ = [
  'Default',
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

class Default(object):
  """ Default values for Pure Data objects """
  def __init__(self):
    self.screen       = { 'x':0, 'y': 22 }
    """ The position of the screen in x-y space """
    
    self.dimension    = { 'width': 450, 'height': 300 }
    """ The size of the screen in pixels """
    
    self.arrdimen     = { 'width': 450, 'height': 278 }
    """ The dimensions of the array in pixels """
    
    self.font         = { 'size': 12, 'face': 0 }
    """ The font size and face """
    
    self.array        = { 'size': 100, 'type': 'float', 'flag': 3}
    """ GOP Array properties """
    
    self.coords       = {
      'range' : {
          'xmin': 0, 
          'xmax': self.array['size'], 
          'ymin': -1, 
          'ymax': 1,
      },
      'gop' : 0,
      'dimen' : {
        'width' : 200,
        'height' : 140
      },
      'margin' : {
        'x' : 0,
        'y' : 0
      }
    }
    """ Coordinates for gop """

    self.vis          = 0
    """ Canvas visibility """
    
    self.digits_width = { 'floatatom': 5, 'symbolatom': 10, 'listbox': 20 } 
    """ Amount of digits/elements to display on the atom box """
    
    self.limits       = { 'lower':0, 'upper':0 } 
    """ Range boundaries for floatatom """
    
    self.flag         = 0
    """ A flag """
    
    self.label        = '-'
    """ Empty symbol for Native Gui """
    self.receive      = '-'
    """ Empty symbol for Native Gui """
    self.send         = '-'
    """ Empty symbol for Native Gui """
    
    self.name         = '(subpatch)'
    """ Empty symbol for nameless patches """
    
    self.iemgui = {
      'label'    : 'empty',
      'fontface' : 0,
      'fontsize' : 10,
      'fgcolor'  : '#000000'
    }
    """ General iemgui properties """
    
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