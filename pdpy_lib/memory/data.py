#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Data Class Definition """

from . import types
from ..core.base import Base
from ..utilities.utils import splitByEscapedChar, log, splitByNone

__all__ = [ 'Data' ]

class Data(Base):
  """ A Data base class """
  
  def __init__(self,
               data=None,
               head=None,
               template=None,
               json=None,
               xml=None):

    self.__pdpy__ = self.__class__.__name__
    super().__init__(pdtype='A', cls=head or '0')
    
    if json is not None:
      super().__populate__(self, json)
    elif xml is not None:
      self.parseXml(xml)
    else:
      if head is not None:
        # 'set' or 'saved' for symbols, otherwise '0' for arrays of floats
        self.__cls__ = str(head)
        self.header = self.__cls__
        if self.__isnum__(self.header):
          self.data = list(map(lambda x: float(x), data))
        elif 'saved' == self.header:
          self.data = list(map(lambda x: str(x), data))
        elif 'set' == self.header:
          self.data = splitByEscapedChar(data, char=';')
          if self.data: # check if the data exists
            # check for name in first element (scalar define)
            if not self.__isnum__(self.data[0].split()[0]):
              self.data = self.data[0].split()
              setattr(self, 'name', self.data.pop(0))
        else:
          log(1,"Unknown data type" + str(head) + " for:\n" + self.__json__())
      else:
        if template is not None:
          self.template = template.name
          self.data = self.fill(template, splitByEscapedChar(data, char=';'))
        elif data is not None:
          self.header = 0
          self.data = super().__setdata__(self, data)
        else:
          raise ValueError("Struct and Data must be present.")
  
  def add(self, attr, value):
    """ Adds a value to the data list in attr """
    if not hasattr(self, attr):
      setattr(self, attr, [])
    getattr(self, attr).append(value)

  def parseXml(self, xml):
    """ Parses the xml string into a pd object """
    if 'header' in xml.attrib:
      self.header = xml.attrib.get('header')
      self.__cls__ = str(self.header)
      data = xml.findall('datum')
      if len(data):
        if self.__isnum__(self.header):
          self.data = [self.__num__(d.text) for d in data]
        elif self.header in ('set', 'saved'):
          self.data = [str(d.text) for d in data]
    else:
      for x in xml.findall('float'):
        self.add('float', types.Float(xml=x))
      for x in xml.findall('symbol'):
        self.add('symbol', types.Symbol(xml=x))
      for x in xml.findall('list'):
        self.add('array', types.List(xml=x))

  def fill(self, template, data):
    """ Fills the data with a template """
    if len(data) == 0: 
      return None

    # log(1,"DATAA", data)
    # log(1,"TEMPLATE", template.__json__())

    def fill_element(target, template, data, attrib='float', cls=types.Float):
      # for k,v in zip(getattr(template, 'float', []), flt):
      #   super().__setdata__(self, Float(v, name=k), 'float')
      if hasattr(template, attrib):
        # log(1,'Filling '+str(attrib).upper(),data)
        for k,v in zip(getattr(template, attrib, []), data):
          super(Data, self).__setdata__(target, cls(v, name=k), attrib)

    def fill_array(target, template, data):
      # log(1,'TEMPLATE',template.name)
      # log(1,'ARRAY',data)
      
      arrays = getattr(template, 'array', [])
      data = splitByNone(data)
      
      for e, d in zip(arrays, data):
        _, _template = template.__p__.getTemplate(e.template)

        if _template is None:
          log(1,"Did not find a template array candidate for: " + template)
          continue
        
        # log(1, 'Filling array', d)
        # log(1, 'Template:', _template.__json__())
        
        pdlist = types.List(name=e.template)
        

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
          
        
        super(Data, self).__setdata__(target, pdlist, 'array')


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
      log(1, "Template " + template.name + " has no float attribute")
      log(1, "Template", template.__json__())
      log(1,'FS',fs)
      

    if flt is not None:
      # log(1,'FILL FLOAT',flt)
      fill_element(self, template, flt, attrib='float', cls=types.Float)
    if sym is not None:
      # log(1,'FILL SYMBOL',sym)
      fill_element(self, template, flt, attrib='symbol', cls=types.Symbol)

    arr = data[1:] if len(data) >= 2 else []
    
    if hasattr(template, 'array') and arr is not []:
      # log(1,'FILL ARRAY',arr)
      # log(1, 'Template', template.__json__())
      fill_array(self, template, arr) # fill the array

  def __pd__(self, template=None):
    """ Parses the pd object into a string """

    if hasattr(self, 'data'):

      if hasattr(self, 'header'):
        if self.__isnum__(self.header):
          s = ' '.join(list(map(lambda x:str(self.__num__(x)), self.data)))
          return super().__pd__(s)
          # return super().__pd__('0 '+s)
        
        if self.header == 'set' or self.header == 'saved':
          self.__cls__ = self.header
          s = ''
          for d in self.data:
            if type(d) in (int, float, str):
              s += str(d)
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
        
        raise ValueError("Unknown type " + str(self.header) + " for:\n" + self.__dumps__())
    
    else:
      
      s = ''
      # call the pd method on every float (PdFLoat) element
      if (hasattr(self, 'float') or hasattr(self, 'floats')) and hasattr(template, 'float'):
        for x in getattr(self, 'float', getattr(self, 'floats', [])):
          s += ' ' + x.__pd__()
      
      # call the pd method on every symbol (Symbol) element
      if (hasattr(self, 'symbol') or hasattr(self, 'symbols'))  and hasattr(template, 'symbol'):
        for x in getattr(self, 'symbol', getattr(self, 'symbols', [])):
          s += ' ' + x.__pd__()
      
      if s != '': s += self.__semi__

      # call the pd method on the array (List) element
      if (hasattr(self, 'array') or hasattr(self, 'arrays')) and hasattr(template, 'array'):
        for x, t in zip(getattr(self, 'array', getattr(self, 'arrays', [])), template.array):
          _, _template = template.__p__.getTemplate(t.template)
          s += ' ' + x.__pd__(_template)
      
      return s

    # return an empty string if nothing else happened    
    return ''


  def __xml__(self, template=None):
    """ Returns the XML Element for this object """

    x = super().__element__(scope=self)
    
    if hasattr(self, 'data'):
  
      if hasattr(self, 'header'):
        super().__update_attrib__(x, 'header', self.header)
      
      if self.__d__.xml['data_as_text']:
        x.text = ' '.join(list(map(lambda x:str(x),self.data)))
      else:
        for d in self.data:
          if isinstance(d, list):
            for dd in d:
              super().__subelement__(x, 'datum', text=str(dd))
          else:
            super().__subelement__(x, 'datum', text=d)

    else:
      # call the xml method on every float (PdFLoat) element
      if hasattr(self, 'float') and hasattr(template, 'float'):
        # flt = super().__element__(tag='floats')
        for e in getattr(self, 'float', []):
          super().__subelement__(x, e.__xml__())
          # super().__subelement__(flt, e.__xml__())
        # super().__subelement__(x, flt)
      
      # call the xml method on every symbol (Symbol) element
      if hasattr(self, 'symbol') and hasattr(template, 'symbol'):
        # sym = super().__element__(tag='symbols')
        for e in getattr(self, 'symbol', []):
          super().__subelement__(x, e.__xml__())
          # super().__subelement__(sym, e.__xml__())
        # super().__subelement__(x, sym)
      
      # call the xml method on the array (List) element
      if hasattr(self, 'array') and hasattr(template, 'array'):
        # arr = super().__element__(tag='arrays')
        for e, t in zip(getattr(self, 'array', []), template.array):
          _, _template = template.__p__.getTemplate(t.template)
          super().__subelement__(x, e.__xml__(_template))
          # super().__subelement__(arr, e.__xml__(_template))
        # super().__subelement__(x, arr)

    return x
