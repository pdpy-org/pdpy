#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

import json
from .base import Base
from ..util.utils import  log, splitByEscapedChar, splitSemi
from .default import GOPArrayFlags

__all__ = [ "Base", "Edge", "Comment", "Coords", "Dependencies", "Graph", "PdArray", "PdMessage", "PdNativeGui", "PdObject", "PdType", "Point", "Size", "Scalar", "Struct" ]


class Point(Base):
  def __init__(self, x, y):
    self.__pdpy__ = self.__class__.__name__
    self.x = self.num(x)
    self.y = self.num(y)

class Size(Base):
  def __init__(self, w, h):
    self.__pdpy__ = self.__class__.__name__
    self.width = self.num(w)
    self.height = self.num(h)

class PdData(Base):
  def __init__(self):
    self.__pdpy__ = self.__class__.__name__
    self.data = []
    return self
  
  def addData(self, data, dtype=float, char=None):
    if char is not None:
      self.data = splitByEscapedChar(data, char=char)
    else:
      self.data = [dtype(d) for d in data]

class PdType(PdData):
  def __init__(self, name, template=None, size=None, flag=None, className=None):
    self.__pdpy__ = self.__class__.__name__
    self.name = name
    self.template = template
    self.size = self.num(size) if size is not None else None
    self.flag = GOPArrayFlags[int(flag)] if flag is not None and flag.isnumeric() else None
    self.className = className

class Struct(Base):
  """ An object containing a Pure Data 'struct' header
  """
  def __init__(self, name, *argv):
    self.__pdpy__ = self.__class__.__name__
    self.name = name
    i = 0

    while i < len(argv):
      
      if i >= len(argv):
        break
      
      pd_type = argv[i]
      pd_name = argv[i + 1]
      
      if "float" == pd_type:
        if not hasattr(self, pd_type):
          self.float = []
        self.float.append(pd_name)
      
      elif "symbol" == pd_type:
        if not hasattr(self, pd_type):
          self.symbol = []
        self.symbol.append(pd_name)
      
      elif "text" == pd_type:
        if not hasattr(self, pd_type):
          self.symbol = []
        self.symbol.append(pd_name)
      
      elif "array" == pd_type:
        if not hasattr(self, pd_type):
          self.array = []
        i += 2
        self.array.append(PdType(pd_name, argv[i]))
      
      else:
        # log(1, self.name, argv)
        log(1, f"Unparsed Struct Field #{i}")
      
      i += 2

class Bounds(Base):
  def __init__(self, lower, upper, dtype=float):
    self.__pdpy__ = self.__class__.__name__
    self.lower = dtype(lower)
    self.upper = dtype(upper)

class Area(Base):
  def __init__(self, coords):
    self.__pdpy__ = self.__class__.__name__
    self.a = Point(coords[0], coords[2])
    self.b = Point(coords[1], coords[3])

class Coords(Base):
  def __init__(self, coords):
    self.__pdpy__ = self.__class__.__name__
    # NON-GOP
    self.range = Area(coords[:4])
    self.dimension = Size(coords[4], coords[5])
    self.gop = self.num(coords[6])
    # GOP
    if 9 == len(coords):
      self.margin = Point(coords[7], coords[8])

class Scalar(PdData):
  def __init__(self, struct, name, *data):
    self.__pdpy__ = self.__class__.__name__
    self.className = "scalar"
    self.name = name
    for s in struct:
      if self.name == s.name:
        if hasattr(s, "float"):
          super().addData(data, char=";")
        elif hasattr(s, "symbol"):
          super().addData(data, char=";")

class Comment(Base):
  def __init__(self, x, y, *argv):
    self.__pdpy__ = self.__class__.__name__
    self.position = Point(x, y)
    # can have \\, split at \\;, and  the unescaped comma is a border flag, f 80
    argc = len(argv)
    argv = list(argv)
    if argc:
      if 2 < len(argv) and "f" == argv[-2] and argv[-1].isnumeric():
        self.border = self.num(argv[-1])
        argv = argv[:-2]
        argv[-1] = argv[-1].replace(",","")
      self.text = splitSemi(argv)

class Dependencies(Base):
  def __init__(self, *argv):
    self.__pdpy__ = self.__class__.__name__
    deps = list(zip(*[iter(argv)]*2))
    for dep in deps:
      if "-path" == dep[0]:
        self.updatePath(dep[1])
      elif "-lib" == dep[0]:
        self.updateLib(dep[1])
  
  def updatePath(self, path):
    if not hasattr(self, "paths"):
      self.paths = []
    self.paths.append(path)
  
  def updateLib(self, lib):
    if not hasattr(self, "libs"):
      self.libs = []
    self.libs.append(lib)
  
  def update(self, deps):
    if hasattr(deps, "paths"):
      if len(deps.paths):
        for path in deps.paths:
          self.updatePath(path)
    if hasattr(deps, "libs"):
      if len(deps.libs):
        for lib in deps.libs:
          self.updateLib(lib)
   
class PdMsg(Base):
  def __init__(self, address):
    self.__pdpy__ = self.__class__.__name__
    self.address = address
  
  def add(self, msg):
    if not hasattr(self, "message"):
      self.message = []
    self.message.append(msg)

class PdMessage(Base):
  def __init__(self, id, x, y, *argv):
    self.__pdpy__ = self.__class__.__name__
    self.className = "msg"
    self.position = Point(x, y)
    self.id = int(id)
    argc = len(argv)
    argv = list(argv)
    
    if argc:
      
        if 2 < len(argv) and "f" == argv[-2] and argv[-1].isnumeric():
          self.border = self.num(argv[-1])
          argv = argv[:-2]
          argv[-1] = argv[-1].replace(",","")
      

        if len(argv) >= 1:
          self.targets = []
          self.targets.append(PdMsg("outlet"))
          i = 0
          msgbuf = ''
          while i < len(argv) :
          
            if "\\," == argv[i]:
              if len(msgbuf) and len(self.targets):
                self.targets[-1].add(msgbuf)
                msgbuf = ''
              else:
                self.targets.pop()
              i += 1
              continue
          
            if "\\;" == argv[i]:
              if len(msgbuf) and len(self.targets):
                self.targets[-1].add(msgbuf)
                msgbuf = ''
              else:
                self.targets.pop()
              if i + 1 < len(argv):
                self.targets.append(PdMsg(argv[i+1]))
              i += 2
              continue

            if len(msgbuf):
              msgbuf += " " + argv[i]
            else:
              msgbuf = argv[i]
            
            i += 1
          
          if len(self.targets):
            self.targets[-1].add(msgbuf)
    
  def addTarget(self, target):
    if not hasattr(self, "targets"):
      self.targets = []
    self.targets.append(PdMsg(target))  

class PdObj(Base):
  """ A PdObj base class 
  
  Description
  -----------
  A PdObj holds the id, and the x and y coordinates of the pd object,
  as well as the arguments array.

  Methods
  -------
  - `addargs(argv)`: Adds arguments to the pd object.
  """
  def __init__(self, id, x, y):
    self.__pdpy__ = self.__class__.__name__
    self.id = int(id)
    self.position = Point(x, y)
  
  def addargs(self, argv):
    if not hasattr(self,'args') or self.args is None: self.args = []
    for arg in argv:
      self.args += [arg]

class PdObject(PdObj, PdData):
  """ A Pure Data Object object
  
  Description
  -----------
  This class represents a Pure Data object.

  Initialization Arguments
  ----------
  The first three arguments correspond to the `PdObj` class.
  1. `id`: The id of the pd object.
  2. `x`: The x-coordinate of the pd object.
  3. `y`: The y-coordinate of the pd object.
  4. `className`: The class name of the pd object.
  5. `args`: The argument `list` of the pd object.

  """
  def __init__(self, *argv):
    super().__init__(*argv[:3])
    args = list(argv)
    argc = len(args)
    try:
      self.className = args[3] if 3 < argc else None
      self.args = args[4:] if 4 < argc else None
    except:
      raise ValueError("Invalid arguments for PdObject")
      # log(1, self.toJSON(), "Can't parse arguments", args)

    self.border = None
    self.__pdpy__ = self.__class__.__name__
  

class PdArray(PdObject):
  """ A Pure Data array object
  
  Description
  -----------
  This class represents a Pure Data array or text object.

  Initialization Arguments
  ----------
  The first four arguments correspond to the `PdObject` arguments. 
  See the `PdObject` class.
  1. `id`: The id of the pd object.
  2. `x`: The x-coordinate of the pd object.
  3. `y`: The y-coordinate of the pd object.
  4. `className`: The class name of the array.
  5. `subclass`: The sub family of the array, eg. `define` or `sum`, etc.
  6. `-k` flag (optional), or `name`: the name of the array
  7. If it is an `array`, then the remaining argument is the array `size`

  Returns
  -------
  A `PdArray` object.
  
  """
  def __init__(self, *argv):
    super().__init__(*argv[:4])
    args = list(argv)
    argc = len(args)
    self.subclass = args[4] if 4 < argc else None
    
    off = 0
    if hasattr(self, "subclass"):
      if "define" == self.subclass:
        
        if 5 < argc:
          if "-k" == args[5]:
            self.keep = True 
            self.name = args[6] if 6 < argc else None
            off += 1
          else:
            self.name = args[5] if 5 < argc else None
            self.keep = False
        
        if "array" == self.className:
          self.size = args[6+off] if 6+off < argc else None
          off += 1
      
    if 6+off < argc:
      self.args = args[6+off:]
    
    self.__pdpy__ = self.__class__.__name__

class PdNativeGui(PdObj):
  """ A Pd Native Gui object 
  
  Description
  -----------
  A Pd Native Gui object is a graphical user interface that is implemented in
  pure data. It is a sublcass of the `PdObj`

  Initialization Arguments
  -----------------------
  1. `className`: the name of the class of the object
  2. id: The id of the object
  3. `x`: The x position of the object
  4. `y`: The y position of the object
  5. `digits_width` : The width of the object in digits
  6. lower limit: The lower limit of the object
  7. upper limit: The upper limit of the object
  8. `flag`: The flag of the object
  9. `label`: The label of the object
  10. `receive`: the receiver symbol of the object
  11. `send`: the sender symbol of the object

  """
  def __init__(self, className, *argv):
    super().__init__(*argv[:3])
    self.__pdpy__ = self.__class__.__name__
    self.className = className
    if 3 < len(argv):
      self.digit_width = argv[3]
      self.limits = Bounds(*argv[4:6])
      self.flag = argv[6] if 6 < len(argv) else None
      if 7 < len(argv):
        self.label = argv[7] if "-" != argv[7] else None
        self.receive = argv[8] if "-" != argv[8] else None
        self.send = argv[9] if "-" != argv[9] else None

class Source(Base):
  def __init__(self, id, port):
    self.__pdpy__ = self.__class__.__name__
    self.id = id
    self.port = port

class Edge(Base):
  """ A Pd Connection 
  Description
  -----------
  A Pd Connection object is a connection between two objects.

  Parameters
  ----------
  1. `source`: The source id of the connection
  2. `port`: The port outlet of the source
  3. `target`: The target id of the connection
  4. `port`: The port inlet of the target
  """
  def __init__(self, srcId, srcPrt, snkId, snkPrt):
    self.__pdpy__ = self.__class__.__name__
    self.source = Source(srcId, srcPrt) 
    self.sink = Source(snkId, snkPrt)
  
class Graph(Base):
  def __init__(self, id, name, area, range):
    self.__pdpy__ = self.__class__.__name__
    self.id = id
    self.name = name
    self.area = Area(area)
    self.range = Area(range)
    self.array = []
    self.border = None
  
  def addArray(self, *argv):
    self.array.append(PdType(argv[0], size = argv[1]))
