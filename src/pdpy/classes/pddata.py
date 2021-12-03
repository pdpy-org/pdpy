#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Canvas Class Definition """

from .base import Base
from .pdtypes import *
from ..util.utils import splitByEscapedChar, log, splitByNone

class PdData(Base):
  """ A PdData base class """
  
  def __init__(self,
               data=None,
               head=None,
               template=None,
               json=None):

    self.__pdpy__ = self.__class__.__name__
    super().__init__(pdtype='A', cls=head)
    
    if json is not None:
      super().__populate__(self, json)
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
    # log(1,"TEMPLATE", template.__json__())

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
      
      arrays = getattr(template, 'array', [])
      data = splitByNone(data)
      
      for e, d in zip(arrays, data):
        _, _template = template.__parent__.getTemplate(e.template)

        if _template is None:
          log(1,f"Did not find a template array candidate for {template}")
          continue
        
        # log(1, 'Filling array', d)
        # log(1, 'Template:', _template.__json__())
        
        pdlist = PdList(name=e.template)
        

        attributes = [ {
          'attr':a,
          'keys':getattr(_template, a)
          } for a in _template.order ]
        # log(1, 'Attributes:', attributes)
        # log(1, 'Length:', len(attributes))
        # log(1, 'Lengths:', lengths)

        for v in d:
          # log(1, 'Filling:', v)
          if len(attributes) == 1:
            attr = attributes[0]['attr']
            keys = attributes[0]['keys']
            # log(1, 'Attr:', attr, 'Keys:', keys)
            for key, val in zip(keys, v):
              # log(1, f"add {attr} element", key, val)
              pdlist.addelement(attr, key, val)
          else:
            for idx, att in enumerate(attributes):
              attr = att['attr']
              keys = att['keys']
              # log(1, 'Keys:', keys, 'Attr:', attr)
              for key in keys:
                # log(1, f"add {attr} element", key, v)
                pdlist.addelement(attr, key, v[idx])
          # TODO: Array recursion ??
          # if hasattr(_template, 'array'):
          #   log(1,'RECURSE ON ARRAY', v)
          #   log(1,'RECURSE ON TEMPLATE', _template.name)
          #   k = getattr(_template, 'array')
          #   # log(1, 'array: keys, values:', k, v)
          #   for key,val in zip(k,v):
          #     # log(1, 'add array element', key, val)
          #     target.addelement('array', key, str(val))
          #   fill_array(target.array, _template, v) # recursion ??????
          
        
        super(PdData, self).__setdata__(target, pdlist, 'array')


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
      # log(1, 'Template', template.__json__())
      fill_array(self, template, arr) # fill the array

  def __pd__(self, template=None):
    """ Parses the pd object into a string """

    if hasattr(self, 'data'):

      if hasattr(self, 'header'):
        if self.header == '0':
          return ' '.join(list(map(lambda x:f"{self.__num__(x)}", self.data)))
        
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
        
        raise ValueError(f"Unknown type {self.header} for:\n{self.__dumps__()}")
    
    else:
     # TODO: order is important here. Template should take priority.
      if template: pass # leave this here for now

      s = ''
      # call the pd method on every float (PdFLoat) element
      if hasattr(self, 'float') and hasattr(template, 'float'):
        for x in getattr(self, 'float', []):
          s += ' ' + x.__pd__()
      
      # call the pd method on every symbol (PdSymbol) element
      if hasattr(self, 'symbol') and hasattr(template, 'symbol'):
        for x in getattr(self, 'symbol', []):
          s += ' ' + x.__pd__()
      
      if s != '': s += self.__semi__

      # call the pd method on the array (PdList) element
      if hasattr(self, 'array') and hasattr(template, 'array'):
        for x, t in zip(getattr(self, 'array', []), template.array):
          _, _template = template.__parent__.getTemplate(t.template)
          s += ' ' + x.__pd__(_template)
      
      return s

    # return an empty string if nothing else happened    
    return ''


  def __xml__(self, template=None):
    """ Returns the XML Element for this object """

    x = super().__element__(self)
    
    if hasattr(self, 'data'):
      data = super().__element__('data')      
      if hasattr(self, 'header'):
        super().__subelement__(data, 'header', self.header)  
      for d in self.data:
        super().__subelement__(data, 'data', d)
      super().__subelement__(x, data)

    else:
      # call the pd method on every float (PdFLoat) element
      if hasattr(self, 'float') and hasattr(template, 'float'):
        # flt = super().__element__('float')
        for e in getattr(self, 'float', []):
          super().__subelement__(x, e.__xml__())
        # super().__subelement__(x, flt)
      
      # call the pd method on every symbol (PdSymbol) element
      if hasattr(self, 'symbol') and hasattr(template, 'symbol'):
        # sym = super().__element__('symbol')
        for e in getattr(self, 'symbol', []):
          super().__subelement__(x, e.__xml__())
        # super().__subelement__(x, sym)
      
      # call the pd method on the array (PdList) element
      if hasattr(self, 'array') and hasattr(template, 'array'):
        # arr = super().__element__('array')
        for e, t in zip(getattr(self, 'array', []), template.array):
          _, _template = template.__parent__.getTemplate(t.template)
          super().__subelement__(x, e.__xml__(_template))
        # super().__subelement__(x, arr)

    return x
