#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Canvas Class Definition """

from .base import Base
from ..util.utils import splitByEscapedChar, log

class PdData(Base):
  """ A PdData base class """
  
  def __init__(self,
               data=None,
               head=None,
               template=None,
               json_dict=None):

    self.__pdpy__ = self.__class__.__name__
    super().__init__(pdtype='A', cls=head)
    
    if json_dict is not None:
      super().__populate__(self, json_dict)
    else:
      if head is not None:
        # 'set' or 'saved' for symbols, otherwise '0' for arrays of floats
        self.__cls__ = str(head)
        self.header = self.__cls__
        if '0' == self.header:
          self.data = [float(d) for d in data]
        elif 'saved' == self.header:
          self.data = [str(d) for d in data]
        elif 'set' == self.header:
          self.data = splitByEscapedChar(data, char=';')
        else:
          log(1,f"Unknown data type {head} for:\n{self.__json__()}")
      else:
        if template is not None:
          self.data = template.parse(splitByEscapedChar(data, char=';'))
        else:
          raise ValueError("Struct and Data must be present.")

  def __pd__(self, template=None):
    """ Parses the pd object into a string """
    if hasattr(self, 'data'):
      
      if self.header == '0':
        return ' '.join(list(map(lambda x:f"{self.num(x)}", self.data)))
      
      if self.header == 'set' or self.header == 'saved':
        self.__cls__ = self.header
        s = ''
        for d in self.data:
          if isinstance(d, str):
            s += d
          else:
            s += ' ' + ' '.join(list(map(lambda x:str(x), d)))
          s += ' \\;'
        return super().__pd__(s)
        # return ' '.join(list(map(lambda x:str(x), self.data)))
      
      # FIXME: this is a hack to get the 'obj' class working as float arrays
      elif self.header == 'obj':
        self.__cls__ = '0'
        s = ' '.join(list(map(lambda x:str(x), self.data)))
        return super().__pd__(s)
      
      if template is not None:
        return template.unparse(self.data)
      
      raise ValueError(f"Unknown type {self.header} for:\n{self.dumps()}")
    else:
      return ''