#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions for Pure Data's Data Structures """

from .base import Base
from .classes import Area # for the Graph class
from .exceptions import ArgumentException
from .default import GOPArrayFlags
from ..util.utils import  log

__all__ = [
  "PdType",
  "Struct",
  "Graph"
]

class PdType(Base):
  """ A Pd Type
  
  Description
  -----------
  A PdType instance extends the Base class with an `addflag` method
  to account for GOPArrayFlags. And, a `__pd__` method to return a
  string representation of the PdType.

  Parameters
  ----------
  json : dict
    A dictionary of the JSON object. For example: 
    ```
    {
      'name' : 'array_name',
      'size' : 100,
      'type' : 'float',
      'flag' : 0,
      'className' : 'goparray'
    }
    ```

  """
  def __init__(self, json=None, **kwargs):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(**kwargs)
    if json is not None:
      super().__populate__(self, json)
    if hasattr(self, 'className') and self.className == 'goparray':
      self.__cls__ = 'array'
    # print("Pdtype", self.__type__, self.__cls__)

  def addflag(self, flag):
    # log(1, "Adding flag: {}".format(flag))
    if flag is not None and flag.isnumeric():
      self.flag = GOPArrayFlags[int(flag)]
    elif flag in GOPArrayFlags:
      self.flag = flag
    else:
      self.flag = None

  def __pd__(self):
    """ Return a string representation of the PdType """
    # log(1, "PdType:", self.__dict__)
    if self.__cls__ == 'array':
      s = super().__pd__(f"{self.name} {self.size} {self.type} {self.flag}")
      for x in getattr(self, 'data', []):
        s += x.__pd__()
      return s
    
    elif hasattr(self, 'template'):
      return f"array {self.name} {self.template}"
    
    else:
      log(1, "PdType: {}".format(self.__cls__))
  
  def __xml__(self):
    """ Return the XML Element for this object """
    x = super().__xml__(scope=self, attrib=('name', 'template', 'size', 'type', 'flag'))
    if hasattr(self, 'data'):
      data = super().__element__('data')
      for d in self.data:
        super().__subelement__(data, 'data', text=d)
      super().__subelement__(x, data)
    return x

class Struct(Base):
  """ An object containing a Pure Data 'struct' header
  """
  def __init__(self, pd_lines=None, json=None, xml_obj=None):
    self.__pdpy__ = self.__class__.__name__
    self.order = []
    super().__init__(pdtype='N', cls='struct')
    if json is not None: 
      super().__populate__(self, json)
    elif xml_obj is not None:
      # log(1,xml_obj.findall('*'))
      self.name = xml_obj.findtext('name')
      for s in xml_obj.findall('float'): self.addFloat(s.text)
      for s in xml_obj.findall('symbol'): self.addSymbol(s.text)
      for s in xml_obj.findall('text'): self.addText(s.text)
      for s in xml_obj.findall('array'): 
        self.addArray(s.findtext('name'),s.findtext('template'))
    elif pd_lines is not None: 
      self.name = pd_lines[0]
      pd_lines = pd_lines[1:]
      i = 0
      while i < len(pd_lines):
        if i >= len(pd_lines): break
        pd_type = pd_lines[i]
        pd_name = pd_lines[i + 1]
        if   'float'  == pd_type: self.addFloat(pd_name)
        elif 'symbol' == pd_type: self.addSymbol(pd_name)
        elif 'text'   == pd_type: self.addText(pd_name)
        elif 'array'  == pd_type:
          array_name = pd_lines[i + 2]
          self.addArray(pd_name, array_name)
          i += 1
        else:
          log(1, f"Unparsed Struct Field #{i}")
          log(1, self.name, pd_lines)
          self.__dumps__()
        i += 2
    else: 
      raise ArgumentException("Struct: Incorrect arguments given")
  
  def addFloat(self, pd_name):
    if not hasattr(self, 'float'):
      self.float = []
      self.order.append('float')
    self.float.append(pd_name)

  def addSymbol(self, pd_name):
    if not hasattr(self, 'symbol'):
      self.symbol = []
      self.order.append('symbol')
    self.symbol.append(pd_name)

  def addText(self, pd_name):
    if not hasattr(self, 'text'):
      self.text = []
      self.order.append('text')
    self.text.append(pd_name)

  def addArray(self, pd_name, array_name):
    """ Append an array structure with symbols for name and template """
    if not hasattr(self, 'array'):
      self.array = []
      self.order.append('array')
    self.array.append(PdType(json={
      'name' : pd_name,
      'template' : array_name
    }))

  def parse(self, data):
    """ Returns a list of scalar data structured by the corresponding struct """
    _data = {}
    # log(1,"DATA",data)
    # data = list(filter(lambda x:x==' ',data))
    if len(data) == 0: 
      return None
    arr = None
    fs = data[0].split(' ')
    # log(1,'FS',fs)
    if len(data) >= 2:
      arr = data[1:]
    # log(1,'ARR',arr)
    
    if hasattr(self, 'float'):
      _data.update({
        'float': {
            f:self.__num__(v) for f,v in zip(self.float, fs[:len(self.float)])
          }
      })
    if hasattr(self, 'symbol'):
      # log(1, "SYMBOLS", self.symbol, fs)
      _data.update({
        'symbol': {f:v for f,v in zip(self.symbol, fs[len(self.float):])}
      })
      # log(1, "DATA", _data)
    
    if arr is not None and hasattr(self, 'array'):
      for a in self.array:
        _, template = self.__parent__.getTemplate(a.template)
        
      if template is not None:
        if hasattr(template, 'float'):
          # fill the corresponding named arrays with float arrays
          _arr_obj = {}
          for val_list in arr:
            # zip key and value from template names and data float values
            for key, val in zip(template.float, val_list):
              if key in _arr_obj:
                _arr_obj[key].append(self.__num__(val))
              else:
                _arr_obj[key] = [self.__num__(val)]
          _data.update({
            'array' : _arr_obj
          })

        if hasattr(template, 'symbol'):
          # fill the corresponding named arrays with tring arrays
          _arr_obj = {}
          for val_list in arr:
            # zip key and value from template names and data string values
            for key, val in zip(template.symbol, val_list):
              if key in _arr_obj:
                _arr_obj[key].append(val)
              else:
                _arr_obj[key] = [val]
          _data.append(_arr_obj)
          
        if hasattr(template, 'array'):
          #TODO: implement this
          log(1,"DS recursion on arrays implemented")
    
    if len(_data):
      return _data

  def __pd__(self):
    """ Returns the struct instruction for the pd file """
    s = self.name

    for a in ('float', 'symbol', 'text'):
      if hasattr(self, a):
        s += ' ' + ' '.join(list(map(lambda x:a+' '+x, getattr(self, a))))
    
    if hasattr(self, 'array'):
      s += ' ' + ' '.join(list(map(lambda x:x.__pd__(), self.array)))
     
    return super().__pd__(s)
  
  def __xml__(self):
    """ Return the XML Element for this object """
    x = super().__element__(self)
    super().__subelement__(x, 'name', text=self.name)
    for a in ('float', 'symbol', 'text'):
      for f in getattr(self, a, []):
        super().__subelement__(x, a, text=f)
    if hasattr(self, 'array'):
      for a in self.array:
        super().__subelement__(x, a.__xml__())
    return x

class Graph(Base):
  """ The ye-olde array """
  def __init__(self, pd_lines=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(cls='graph')

    if pd_lines is not None:
      self.id = pd_lines[0]
      self.name = pd_lines[1]
      self.area = Area(pd_lines[2:6])
      self.range = Area(pd_lines[6:10])
    elif json is not None:
      super().__populate__(self, json)
    elif xml is not None:
      self.id = xml.findtext('id')
      self.name = xml.findtext('name')
      self.area = Area(xml=xml.find('area'))
      self.range = Area(xml=xml.find('range'))
 
  def addArray(self, *args):
    """ Append an array structure with symbols for name and template """
    if not hasattr(self, 'array'):
      self.array = []

    self.array.append({
      'name' : args[1],
      'size' : self.__num__(args[2]),
      'type' : args[3]
    })

  def __pd__(self):
    """ Returns the graph instruction for the pd file """
    s = self.name
    s += ' ' + self.range.__pd__(order=1)
    s += ' ' + self.area.__pd__(order=1)
    s = super().__pd__(s)
    for x in getattr(self, 'array', []):
      s += f"#X array {x['name']} {x['size']} {x['type']}"
      s += self.__end__
    s += '#X pop' + self.__end__
    return s

  def __xml__(self):
    """ Return the XML Element for this object """

    x = super().__xml__(scope=self, attrib=('name','area','range'))

    for a in getattr(self, 'array', []):
      arr = super().__element__(a)
      for y in ('name', 'size', 'type'):
        super().__subelement__(arr, y, text=a[y])
      super().__subelement__(x, arr)
    return x

