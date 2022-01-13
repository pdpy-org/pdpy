#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #

__all__ = ['XmlTagConvert']

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
    # print(f"to_xml_tag(): {key} --> {tag}")
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
