#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

from .base import Base
from .data_structures import PdData, PdType
from ..util.utils import splitSemi

__all__ = [ 
  "Base",
  "Edge",
  "Comment",
  "Coords",
  "Dependencies",
  "Graph",
  "PdArray",
  "PdNativeGui",
  "PdObject",
  "Point",
  "Size"
]

class Point(Base):
  def __init__(self, x=None, y=None, json_dict=None):
    self.__pdpy__ = self.__class__.__name__
    if x is not None and y is not None:
      self.x = self.num(x)
      self.y = self.num(y)
    elif isinstance(json_dict, dict):
      self.x = self.num(json_dict.get("x", None))
      self.y = self.num(json_dict.get("y", None))
    else:
      self.x = None
      self.y = None
class Size(Base):
  def __init__(self, w=None, h=None, json_dict=None):
    self.__pdpy__ = self.__class__.__name__
    if w is not None and h is not None:
      self.width = self.num(w)
      self.hheight = self.num(h)
    elif isinstance(json_dict, dict):
      self.width = self.num(json_dict.get("width", None))
      self.hheight = self.num(json_dict.get("height", None))
    else:
      self.width = None
      self.hheight = None

class Bounds(Base):
  def __init__(self, lower=None, upper=None, dtype=float, json_dict=None):
    self.__pdpy__ = self.__class__.__name__
    if lower is not None and upper is not None:
      self.lower = dtype(lower)
      self.upper = dtype(upper)
    elif isinstance(json_dict, dict):
      self.lower = dtype(json_dict.get("lower", 0))
      self.upper = dtype(json_dict.get("upper", 0))
    else:
      self.lower = dtype(0)
      self.upper = dtype(0)

class Area(Base):
  """ 
  Area
  ====
  
  Description
  -----------
  Represents an area with two points. See ::class::`Point`.
  The first two coordinates are the upper left corner `a`,
  and the second two are the upper lower corner, `b`.
  a ------------------- |
  |                     |
  |                     |
  |                     v
  |-------------------> b
  """
  def __init__(self, coords=None, json_dict=None):
    self.__pdpy__ = self.__class__.__name__
    if coords is not None:
      self.a = Point(x=coords[0], y=coords[1])
      self.b = Point(x=coords[2], y=coords[3])
    elif isinstance(json_dict, dict):
      self.a = Point(json_dict=json_dict.get("a", None))
      self.b = Point(json_dict=json_dict.get("b", None))
    else:
      self.a = Point()
      self.b = Point()
  

class Coords(Base):
  """ 
  Coordinates of the Pd Patch
  ===========================

  Description
  ----------
  The coordinates of the Pd Patch takes a list of 7 or 9 arguments 
  Created in the following format:
  - `range` : first 4 floats are the Area. Defined by 2 Points. See ::class::`Area` and ::class::`Point`.
  - `dimension` : next 2 floats are the Size. See ::class::`Size`.
  - `gop` : next 1 int (0 or 1) defines if it must Graph-on-Parent.
  - `margin` : if present, next 2 floats are the margins. See ::func::`addmargin`)

  """
  def __init__(self, coords=None, json_dict=None):
    self.__pdpy__ = self.__class__.__name__
    if coords is not None:
      # NON-GOP
      self.range = Area(coords=coords[:4])
      self.dimension = Size(w=coords[4], h=coords[5])
      self.gop = self.num(coords[6])
      # GOP
      if 9 == len(coords):
        self.addmargin(x=coords[7], y=coords[8])
    elif isinstance(json_dict, dict):
      self.range = Area(json_dict=json_dict.get("range", None))
      self.dimension = Size(json_dict=json_dict.get("dimension", None))
      self.gop = self.num(json_dict.get("gop", 0))
      if hasattr(json_dict, 'margin'):
        self.addmargin(json_dict=json_dict.get("margin", None))
    else:
      self.range = Area()
      self.dimension = Size()
      self.gop = 0
      self.margin = Size()

  def addmargin(self, x=None, y=None, json_dict=None):
    self.margin = Point(x=x, y=y, json_dict=json_dict)

class Comment(Base):
  def __init__(self, x, y, *argv):
    self.__pdpy__ = self.__class__.__name__
    self.position = Point(x=x, y=y)
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
    # python magic to split a list in pairs
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

class PdObj(PdData):
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
    self.position = Point(x=x, y=y)
  
  def addargs(self, argv):
    if not hasattr(self,'args') or self.args is None: 
      self.args = []
    for arg in argv:
      self.args += [arg]

class PdObject(PdObj):
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
          self.size = int(args[6+off]) if 6+off < argc else None
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
