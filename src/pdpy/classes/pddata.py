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
               struct=None,
               json_dict=None):

    self.__pdpy__ = self.__class__.__name__
    super().__init__(pdtype='A', cls=head)
    
    if json_dict is not None:
      super().__populate__(self, json_dict)
    else:
      self.struct = struct

      if head is not None:
        # 'set' or 'saved' for symbols, otherwise '0' for arrays of floats
        self.__cls__ = str(head)

        if '0' == self.__cls__:
          self.data = [float(d) for d in data]
        elif 'saved' == self.__cls__:
          self.data = [str(d) for d in data]
        elif 'set' == self.__cls__:
          self.data = splitByEscapedChar(data, char=';')
        else:
          raise ValueError(f"Unknown data type {head} for:\n{self.dumps()}")
      else:
        if self.struct is not None:
          self.data = struct.parse(splitByEscapedChar(data, char=';'))
        else:
          raise ValueError("Struct and Data must be present.")


  def __pd__(self, template=None):
    """ Parses the pd object into a string """
    if hasattr(self, 'data'):
      if self.__cls__ == 0:
        return ' '.join(list(map(lambda x:f"{self.num(x)}", self.data)))
      elif self.__cls__ == 'set' or self.__cls__ == 'saved':
        return ' '.join(list(map(lambda x:str(x), self.data)))
      elif self.__cls__ == 'obj':
        s = ' '.join(list(map(lambda x:str(x), self.data)))
        return super().__pd__(s)
      elif template is not None:
        return template.unparse(self.data)
      else:
        raise ValueError(f"Unknown type {self.__cls__} for:\n{self.dumps()}")
    else:
      return ''