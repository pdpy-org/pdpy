#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #

__all__ = [ 'XmlTagConvert' ]

class XmlTagConvert(object):
  def __init__(self):    
    self.__table__ = {
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
    self.__tilde__ = "~"
    self.___tilde__ = "_tilde"
  
  def find(self, element, string):
    result = element in string
    # print('find', element, string, result)
    return result

  def to_tilde(self, tag):
    """ Returns the tag name replacing tilde char with _tilde """
    
    if not self.find(self.__tilde__, tag):
      return tag
    s = str(tag).replace(self.__tilde__, self.___tilde__)
    # print(f"to_tilde(): {tag} --> {s}")
    return s

  def from_tilde(self, tag):
    """ Returns the tag name replacing _tilde with tilde char """
    if not self.find(self.___tilde__, tag):
      return tag
    s = str(tag).replace(self.___tilde__, self.__tilde__)
    # print(f"from_tilde(): {tag} --> {s}")
    return s

  def to_xml_tag(self, key):
    """ Returns the tag name replacing special characters """
    # print(f"to_xml_tag(): {key}")
    tag = key
    if self.find(self.__tilde__, key):
      key_notilde = str(key).replace(self.__tilde__, '')
      if key_notilde in self.__table__:
        tag = self.__table__[key_notilde]
      else:
        # print(f'to_xml_tag(): tilde {key} not in table:', key)
        pass
      tag = self.to_tilde(tag)
    else:
      if key in self.__table__:
        tag = self.__table__[key]
      else:
        for k, v in self.__table__.items():
          if k in key:
            tag = v
            break
        # print('to_xml_tag(): key not in table:', key)
        tag = key
    # print(f"to_xml_tag(): {key} --> {tag}")
    # argh, we need to check again for internal characters, eg: <mul_*_tilde>
    for i,e in enumerate(tag):
      for k in self.__table__.keys():
        if e == k:
          tag = tag[:i] + self.__table__[k] + tag[i+1:]
          break
    return tag

  def to_pd_obj(self, pd_key):
    """ Returns the tag name replacing special characters """
    _tag = self.from_tilde(pd_key)
    for key, value in self.__table__.items():
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
