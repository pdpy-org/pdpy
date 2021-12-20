#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions for Pure Data's Data Structures """

from .base import Base
from .pddata import PdData

__all__ = [
  "Scalar"
]

# TODO: so, what if we just fill the Struct with the scalar data
# instead of this Scalar class? maybe forget this class and use only Struct?
# Not really, though. Let's just use one Struct to define many scalars, 
# like pd does.

class Scalar(Base):
  def __init__(self, 
               struct=None,
               pd_lines=None,
               json=None,
               xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(cls='scalar')
    self.className = self.__cls__
    
    if pd_lines is not None:
      self.parsePd(struct, pd_lines)
    elif json is not None:
      super().__populate__(self, json)
    # elif xml is not None:
    #   self.parseXml(struct, xml)

  # def parseXml(self, struct, argv):
  #   self.name = argv.findtext('name')
  #   _data = argv.find('data')
  #   if _data:
  #     _symbol = _data.find('symbol')
  #     _array  = _data.find('array')
  #     _float  = _data.find('float')
  #     for s in struct:
  #       if self.name == s.name:
  #         if _symbol:
  #           setattr(self, 'data',PdData(data = _symbol.text, template = s))
  #         if _float:
  #           setattr(self, 'data',PdData(data = _float.text, template = s))
  #         if _array:
  #           setattr(self, 'data',PdData(data = list(map(lambda x:x.text, _array.findall('*'))), template = s))

  def parsePd(self, struct, argv):
    self.name = argv[0]
    for s in struct:
      if self.name == s.name:
        setattr(self, 'data', PdData(data = argv[1:], template = s))
    
  def __pd__(self):
    """ Returns the data of this scalar as a pd string """
    if hasattr(self, 'data'):
      _, template = super().__getroot__(self).getTemplate(self.name)
      return super().__pd__(self.name + ' ' + self.data.__pd__(template))
    else:
      return super().__pd__(self.name)

  def __xml__(self):
    """ Returns the XML Element for this objcet """
    x = super().__element__(self)
    super().__subelement__(x, 'name', text=self.name)
    if hasattr(self, 'data'):
      _, template = super().__getroot__(self).getTemplate(self.name)
      super().__subelement__(x, self.data.__xml__(template))
    return x