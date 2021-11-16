#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions for Pure Data's Data Structures """

from .base import Base
from .classes import Area # for the Graph class
from .default import GOPArrayFlags
from ..util.utils import  log

__all__ = [
  "PdType",
  "Struct",
  "Graph",
  "Scalar"
]

class PdType(Base):
  def __init__(self, json_dict = None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__()
    if json_dict is not None:
      super().__populate__(self, json_dict)
    # self.name = name
    # self.template = template
    # self.size = self.num(size) if size is not None else None
    # self.addflag(flag)
    # self.className = className
  
  def addflag(self, flag):
    # log(1, "Adding flag: {}".format(flag))
    if flag is not None and flag.isnumeric():
      self.flag = GOPArrayFlags[int(flag)]
    elif flag in GOPArrayFlags:
      self.flag = flag
    else:
      self.flag = None


  # def __pd__(self):
  #   elif "goparray" == className:
  #   s += "#X array"
  #   s += ' ' + getattr(x,'name')
  #   s += ' ' + str(getattr(x,'size'))
  #   s += ' float'
  #   s += ' ' + str(GOPArrayFlags.index(getattr(x,'flag')))

class Struct(Base):
  """ An object containing a Pure Data 'struct' header
  """
  def __init__(self, pd_lines=None, json_dict=None, xml_obj=None):
    self.__pdpy__ = self.__class__.__name__
    
    if   pd_lines is not None: 
      self.parsePd(pd_lines)
    elif json_dict is not None: 
      super().__populate__(self, json_dict)
    elif xml_obj is not None:
      self.parseXML(xml_obj)
    else: 
      log(1, f"Unsupported arguments")
  
  def parent(self, parent=None):
    """ Sets the parent of this object if `parent` is present, otherwise returns the parent of this object."""
    if parent is not None:
      self.__parent__ = parent
      return self
    elif self.__parent__ is not None:
      return self.__parent__
    else:
      raise ValueError("No parent set")

  def parsePd(self, argv):
    self.name = argv[0]
    argv = argv[1:]
    
    i = 0

    while i < len(argv):
      if i >= len(argv): break
      pd_type = argv[i]
      pd_name = argv[i + 1]
      
      if   'float'  == pd_type: self.addFloat(pd_name)
      elif 'symbol' == pd_type: self.addSymbol(pd_name)
      elif 'text'   == pd_type: self.addSymbol(pd_name)
      elif 'array'  == pd_type:
        i += 2
        self.addArray(pd_name, argv[i])
      else:
        # log(1, self.name, argv)
        log(1, f"Unparsed Struct Field #{i}")
      
      i += 2
  
  # def parseJson(self, x):
  #   # x is the simple namespace
  #   for key, value in x.__dict__.items():

  #     if key == 'float':
  #       for v in value:
  #         self.addFloat(v)
      
  #     if key == 'symbol' or key == 'text':
  #       for v in value:
  #         self.addSymbol(v)
      
  #     if key == 'array':
  #       for v in value:
  #         self.addArray(v.name, v.template)

  def parseXML(self, x):
    # x is the xml object
    # log(1,x.findall('*'))
    self.name = x.findtext('name')
    for s in x.findall('float'): self.addFloat(s.text)
    for s in x.findall('symbol'): self.addSymbol(s.text)
    for s in x.findall('text'): self.addSymbol(s.text)
    for s in x.findall('array'): 
      self.addArray(s.findtext('name'),s.findtext('template'))
  
  def addFloat(self, pd_name):
    if not hasattr(self, 'float'):
      self.float = []
    self.float.append(pd_name)

  def addSymbol(self, pd_name):
    if not hasattr(self, 'symbol'):
      self.symbol = []
    self.symbol.append(pd_name)

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
    _arr = None
    _fs = data[0].split(' ')
    # log(1,'FS',_fs)
    if len(data) > 2:
      _arr = data[1:]
    # log(1,'ARR',_arr)
    
    if hasattr(self, 'float'):
      _data.append({f:self.num(v) for f,v in zip(self.float, _fs[:len(self.float)])})
    if hasattr(self, 'symbol'):
      log(1, "SYMBOLS", self.symbol, _fs)
      _data.append({f:v for f,v in zip(self.symbol, _fs[len(self.float)+1:])})
    
    if _arr is not None and hasattr(self, 'array'):
      for a in self.array:
        _, template = self.__parent__.getTemplate(a.template)
        
      if template is not None:
        if hasattr(template, 'float'):
          # fill the corresponding named arrays with float arrays
          _arr_obj = {}
          for val_list in _arr:
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
          for val_list in _arr:
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

  def from_json(self, json_data):
    """ Returns a pd scalar structured by the corresponding struct """
    # log(1, "JSON", json_data.__dict__['data'])
    # json_data is the simple namespace
    _data = []
    data = json_data.__dict__['data']
    if not len(data):
      return None
    _fs = data[0].__dict__
    _arr = None
    if len(data) > 2:
      _arr = map(lambda x:x.__dict__, data[1:])

    if hasattr(self, 'float'):
      _data.append({f:self.num(_fs[f]) for f in self.float})
    if hasattr(self, 'symbol'):
      _data.append({f:_fs[f] for f in self.float})
    
    if _arr is not None and hasattr(self, 'array'):
      for a in self.array:
        _, _template = self.__parent__.getTemplate(a.template)
        if _template is not None:
      
          if hasattr(_template, 'float'):
            for val_list in _arr:
              _data.append({f:self.num(val_list[f]) for f in _template.float})
      
          if hasattr(_template, 'symbol'):
            for val_list in _arr:
              _data.append({f:val_list[f] for f in _template.symbol})
          
          if hasattr(_template, 'array'):
            #TODO: implement this
            log(1,"DS recursion on arrays implemented")
      
    if len(_data):
      return _data

class Graph(Struct):
  """ The ye-olde array """
  def __init__(self, pd_lines=None, json_dict=None, xml_object=None):
    self.__pdpy__ = self.__class__.__name__
    if pd_lines is not None:
      self.id = pd_lines[0]
      self.name = pd_lines[1]
      self.area = Area(pd_lines[2:5])
      self.range = Area(pd_lines[5:8])
      self.border = None
    elif json_dict is not None:
      super().__populate__(self, json_dict)
    elif xml_object is not None:
      self.id = xml_object.findtext('id')
      self.name = xml_object.findtext('name')
      self.area = Area(xml_object=xml_object.find('area'))
      self.range = Area(xml_object=xml_object.find('range'))
      self.border = None

# TODO: so, what if we just fill the Struct with the scalar data
# instead of this Scalar class? maybe forget this class and use only Struct?

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
            super().__fill__(_symbol.text, dtype=str)
            # super().__fill__(map(lambda x:x.text, _data.findall('symbol')))
          if _float:
            super().__fill__(_float.text, dtype=float)
            # super().__fill__(map(lambda x:x.text, _data.findall('float')))
          if _array:
            super().__fill__(map(lambda x:x.text, _array.findall('*')))

  def parsePd(self, struct, argv):
    self.name = argv[0]
    for s in struct:
      if self.name == s.name:
        # print('parsing struct', argv)
        super().__fill__(argv[1:], char=";")
        super().__fill__(s.parse(self.data))

  def __pd__(self):

    s = self.name

    _arr = None
    if not hasattr(self, 'data'):
      log(1,'Scalar has no data')
      self.dumps()

    _fs = self.data[0]
    # log(1,'DATA',self.data)
    if len(self.data) > 2:
      _arr = self.data[1:]

    if hasattr(self.__struct__,'float'):
      for f in getattr(self.__struct__,'float'):
        if f in _fs:
          s += ' ' + str(_fs[f]) + ' \\;'
    
    if hasattr(self.__struct__,'symbol'):
      for f in getattr(self.__struct__,'symbol'):
        if f in _fs:
          s += ' ' + str(_fs[f]) + ' \\;'
    
    if _arr is not None and hasattr(self.__struct__,'array'):
      for a in getattr(self.__struct__,'array'):
        _,  _template = self.__struct__.getTemplate(getattr(a,'template'))
        if _template is not None:

          if hasattr(_template, 'float'):
            # populate de pd string by the structs' order
            _arr_str = ''
            for val_list in _arr:
              for idx in enumerate(getattr(_template, 'float')):
                  _arr_str += ' ' + val_list[idx]
            s += ' ' + _arr_str + ' \\;'
          
          if hasattr(_template, 'symbol'):
            # populate de pd string by the structs' order
            _arr_str = ''
            for val_list in _arr:
              for idx in enumerate(getattr((_template, 'symbol'))):
                  _arr_str += ' ' + val_list[idx]
            s += ' ' + _arr_str + ' \\;'
          
          if hasattr(_template, 'array'):
            #TODO: implement this
            log(1,"DS recursion on arrays implemented")
    
    return super().__pd__(s)

