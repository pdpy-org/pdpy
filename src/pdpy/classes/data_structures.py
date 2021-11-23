#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions for Pure Data's Data Structures """

from .base import Base
from .classes import Area # for the Graph class
from .exceptions import ArgumentException
from .pddata import PdData
from .default import GOPArrayFlags
from ..util.utils import  log

__all__ = [
  "PdType",
  "Struct",
  "Graph",
  "Scalar"
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
  json_dict : dict
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
  def __init__(self, json_dict=None, **kwargs):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(**kwargs)
    if json_dict is not None:
      super().__populate__(self, json_dict)
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

class Struct(Base):
  """ An object containing a Pure Data 'struct' header
  """
  def __init__(self, pd_lines=None, json_dict=None, xml_obj=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(pdtype='N', cls='struct')
    if json_dict is not None: 
      super().__populate__(self, json_dict)
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
          self.dumps()
        i += 2
    else: 
      raise ArgumentException("Struct: Incorrect arguments given")
  
  def addFloat(self, pd_name):
    if not hasattr(self, 'float'):
      self.float = []
    self.float.append(pd_name)

  def addSymbol(self, pd_name):
    if not hasattr(self, 'symbol'):
      self.symbol = []
    self.symbol.append(pd_name)

  def addText(self, pd_name):
    if not hasattr(self, 'text'):
      self.text = []
    self.text.append(pd_name)

  def addArray(self, pd_name, array_name):
    """ Append an array structure with symbols for name and template """
    if not hasattr(self, 'array'):
      self.array = []
    self.array.append(PdType(json_dict={
      'name' : pd_name,
      'template' : array_name
    }))

  def parse(self, data):
    """ Returns a list of scalar data structured by the corresponding struct """
    _data = []
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
      _data.append({f:self.num(v) for f,v in zip(self.float, fs[:len(self.float)])})
    if hasattr(self, 'symbol'):
      # log(1, "SYMBOLS", self.symbol, fs)
      _data.append({f:v for f,v in zip(self.symbol, fs[len(self.float):])})
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
                _arr_obj[key].append(self.num(val))
              else:
                _arr_obj[key] = [self.num(val)]
          _data.append(_arr_obj)

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

  def unparse(self, data):
    """ Returns a pd scalar structured by the corresponding struct """
   
    if not len(data): return ''
    
    s = ''
    # fs = data[0]
    # arr = None
    # if len(data) >= 2:
      # arr = data[1:]
    # log(1,"DATA",data)
    # log(1,'FS',fs)
    # log(1,'ARR',arr)
    for d in data:
      if isinstance(d, dict):
        if hasattr(self, 'float'):
          s += ' '.join([str(d[f]) for f in self.float if f in d])
          s += ' \\;'
        if hasattr(self, 'symbol'):
          s += ' '.join([str(d[f]) for f in self.symbol if f in d])
          s += ' \\;'
      else:
        if hasattr(self, 'array'):
          # find the correct template
          for a in self.array:
            _, _template = self.__parent__.getTemplate(a.template)
          # if we found it, go on:
          if _template is not None:
            for x in d:
              for f in getattr(_template, 'float', []):
                val = x[f]
                if isinstance(val, list):
                  s += f"{' '.join(list(map(lambda x:str(x),val)))}"
                else:
                  s += f"{val}"
              for f in getattr(_template, 'symbol', []):
                val = x[f]
                if isinstance(val, list):
                  s += f"{' '.join(list(map(lambda x:str(x),val)))}"
                else:
                  s += f"{val}"
              s += ' \\;'
            if hasattr(_template, 'array'):
              #TODO: implement this
              log(1,"DS recursion on arrays implemented")
    if len(s):
      return s

  def __pd__(self):
    """ Returns the struct instruction for the pd file """
    s = self.name

    for a in ['float', 'symbol', 'text']:
      if hasattr(self, a):
        s += ' ' + ' '.join(list(map(lambda x:a+' '+x, getattr(self, a))))
    
    if hasattr(self, 'array'):
      s += ' ' + ' '.join(list(map(lambda x:x.__pd__(), self.array)))
     
    return super().__pd__(s)

class Graph(Struct):
  """ The ye-olde array """
  def __init__(self, pd_lines=None, json_dict=None, xml_object=None):
    self.__pdpy__ = self.__class__.__name__
    if pd_lines is not None:
      self.id = pd_lines[0]
      self.name = pd_lines[1]
      self.area = Area(pd_lines[2:5])
      self.range = Area(pd_lines[5:8])
    elif json_dict is not None:
      super().__populate__(self, json_dict)
    elif xml_object is not None:
      self.id = xml_object.findtext('id')
      self.name = xml_object.findtext('name')
      self.area = Area(xml_object=xml_object.find('area'))
      self.range = Area(xml_object=xml_object.find('range'))
    
# TODO: so, what if we just fill the Struct with the scalar data
# instead of this Scalar class? maybe forget this class and use only Struct?
# Not really, though. Let's just use one Struct to define many scalars, 
# like pd does.

class Scalar(Base):
  def __init__(self, 
               struct=None,
               pd_lines=None,
               json_dict=None,
               xml_object=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(cls='scalar')
    self.className = self.__cls__
    
    if pd_lines is not None:
      self.parsePd(struct, pd_lines)
    elif json_dict is not None:
      super().__populate__(self, json_dict)
    elif xml_object is not None:
      self.parseXml(struct, xml_object)

  def parseXml(self, struct, argv):
    self.name = argv.findtext('name')
    _data = argv.find('data')
    if _data:
      _symbol = _data.find('symbol')
      _array  = _data.find('array')
      _float  = _data.find('float')
      for s in struct:
        if self.name == s.name:
          if _symbol:
            setattr(self, 'data',PdData(data = _symbol.text, template = s))
          if _float:
            setattr(self, 'data',PdData(data = _float.text, template = s))
          if _array:
            setattr(self, 'data',PdData(data = list(map(lambda x:x.text, _array.findall('*'))), template = s))

  def parsePd(self, struct, argv):
    self.name = argv[0]
    for s in struct:
      if self.name == s.name:
        # print('parsing struct', argv)
        setattr(self, 'data', PdData(data = argv[1:],template = s))

  def __pd__(self):

    s = self.name
    for x in getattr(self, 'data', []):
      _, template = self.getroot(self).getTemplate(self.name)
      s += ' ' + template.unparse(x.data)
    return super().__pd__(s)
