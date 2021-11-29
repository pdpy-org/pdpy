#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Canvas Class Definition """

from .base import Base
from .pdtypes import *
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
          self.template = template.name
          self.data = self.fill(template, splitByEscapedChar(data, char=';'))
        else:
          raise ValueError("Struct and Data must be present.")

  def fill(self, template, data):
    """ Fills the data with a template """
    if len(data) == 0: 
      return None

    # log(1,"DATAA", data)

    def fill_element(target, template, data, attrib='float', cls=PdFloat):
      # for k,v in zip(getattr(template, 'float', []), flt):
      #   super().__setdata__(self, PdFloat(v, name=k), 'float')
      if hasattr(template, attrib):
        # log(1,'Filling '+str(attrib).upper(),data)
        for k,v in zip(getattr(template, attrib, []), data):
          super(PdData, self).__setdata__(target, cls(v, name=k), attrib)

    def fill_array(target, template, data):
      # log(1,'TEMPLATE',template.name)
      # log(1,'ARRAY',data)

      for e in getattr(template, 'array', []):
        _, _template = template.__parent__.getTemplate(e.template)
      
      if _template is None:
        log(1, f"Did not find a template candidate for an array in {template}")
        return None
      # isthere=False
      if hasattr(target, 'array'):
        pdlist = getattr(target, 'array')
        # isthere=True
      else:
        pdlist = PdList()
        setattr(target, 'array', pdlist)

      # log(1, "Filling array",isthere, pdlist.__json__())

      for v in data:
        
        if hasattr(_template, 'float'):
          k = getattr(_template, 'float')
          # log(1, 'float: keys, values:', k, v)
          for key,val in zip(k,v):
            # log(1, 'add float element', key, val)
            pdlist.addelement('float', key, self.num(val))
        
        if hasattr(_template, 'symbol'):
          k = getattr(_template, 'symbol')
          # log(1, 'symbol: keys, values:', k, v)
          for key,val in zip(k,v):
            # log(1, 'add symbol element', key, val)
            pdlist.addelement('symbol', key, str(val))
        

        # if hasattr(_template, 'array'):
        #   log(1,'RECURSE ON ARRAY', v)
        #   log(1,'RECURSE ON TEMPLATE', _template.name)
        #   k = getattr(_template, 'array')
        #   # log(1, 'array: keys, values:', k, v)
        #   for key,val in zip(k,v):
        #     # log(1, 'add array element', key, val)
        #     target.addelement('array', key, str(val))
        #   fill_array(target.array, _template, v) # recursion ??????
        

    fs = data[0].split(' ')
    
    if hasattr(template, 'float') and hasattr(template, 'symbol'):

      flt = fs[:len(template.float)]
      sym = fs[len(template.float):]
    
    elif hasattr(template, 'float'):
      flt = fs[:len(template.float):]
      sym = None

    elif hasattr(template, 'symbol'):
      flt = None
      sym = fs[:len(template.symbol):]

    else:
      log(1, f"Template {template.name} has no float attribute")
      log(1, "Template", template.__json__())
      log(1,'FS',fs)
      

    if flt is not None:
      # log(1,'FILL FLOAT',flt)
      fill_element(self, template, flt, attrib='float', cls=PdFloat)
    if sym is not None:
      # log(1,'FILL SYMBOL',sym)
      fill_element(self, template, flt, attrib='symbol', cls=PdSymbol)

    arr = data[1:] if len(data) >= 2 else []
    
    if hasattr(template, 'array') and arr is not []:
      # log(1,'FILL ARRAY',arr)
      fill_array(self, template, arr) # fill the array

    # self.dumps()
    # log(1, '=' * 60)


  def __pd__(self, template=None):
    """ Parses the pd object into a string """

    if hasattr(self, 'data'):

      if hasattr(self, 'header'):
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
        
        # FIXME: this is a hack to get the 'obj' class working as float arrays
        elif self.header == 'obj':
          self.__cls__ = '0'
          s = ' '.join(list(map(lambda x:str(x), self.data)))
          return super().__pd__(s)
        
      else:
        
        raise ValueError(f"Unknown type {self.header} for:\n{self.dumps()}")
    
    else:
     # TODO: order is important here. Template should take priority.
      if template: pass # leave this here for now

      s = ''
      # call the pd method on every float (PdFLoat) element
      if hasattr(self, 'float') and hasattr(template, 'float'):
        for x in getattr(self, 'float', []):
          s += ' ' + x.__pd__()
        s += ' \\;'
      
      # call the pd method on every symbol (PdSymbol) element
      if hasattr(self, 'symbol') and hasattr(template, 'symbol'):
        for x in getattr(self, 'symbol', []):
          s += ' ' + x.__pd__()
        s += ' \\;'
      
      # call the pd method on the array (PdList) element
      if hasattr(self, 'array') and hasattr(template, 'array'):
        s += ' ' + self.array.__pd__(template)

      return s

    # return an empty string if nothing else happened    
    return ''