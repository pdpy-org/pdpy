#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

import json
from ..util.utils import  log, splitAtChar, splitByEscapedChar, splitSemi

__all__ = [ "Base", "Edge", "Comment", "Coords", "Dependencies", "Graph", "IEMGuiNames", "PdArray", "PdIEMGui", "PdMessage", "PdNativeGui", "PdObject", "PdType", "Point", "Size", "Scalar", "Struct", "GOPArrayFlags", "IEMGuiNames", "PdFonts"]

GOPArrayFlags = [
  "polygon", "polygon-saved",
  "points", "points-saved",
  "bezier", "bezier-saved",
]
IEMGuiNames = [
  "hsl",
  "vsl",
  "cnv",
  "nbx",
  "hradio",
  "vradio",
  "vu",
  "tgl",
  "bng"
]
PdFonts = [
  "Menlo",
  "Helvetica",
  "Times"
]


def filter_underscores(o):
  return { 
    k : v 
    for k,v in o.__dict__.items() 
    if not k.startswith("__") or k=="__pdpy__"
  }


class Base(object):
  def __init__(self):
    self.patchname = None
    return self
  
  def __setattr__(self, name, value):
    if value is not None:
        self.__dict__[name] = value

  def toJSON(self):
    return json.dumps(self,
      default=filter_underscores,
      sort_keys=False,
      indent=4)
  
  def dumps(self):
    print(self.toJSON())

  def num(self, n):
    pdnm = None
    if isinstance(n, str):
      if "#" in n: pdnm = n # skip css-style colors preceded by '#'
      elif ("e" in n or "E" in n) and ("-" in n or "+" in n):
        pdnm = "{:e}".format(int(float(n)))
      elif "." in n: pdnm = float(n)
      else:
        pdnm = int(n)
    else:
      pdnm = n
    return pdnm

  def pdbool(self, n):
    return bool(int(float(n)))

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
    self.id = id
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

class PdObj(Base):
  def __init__(self, id, x, y):
    self.__pdpy__ = self.__class__.__name__
    self.id = id
    self.position = Point(x, y)
  
  def addargs(self, argv):
    if not hasattr(self,'args') or self.args is None: self.args = []
    for arg in argv:
      # print("adding",arg)
      self.args += [arg]
    # print("ARGS",self.args)

class PdObject(PdObj, PdData):
  def __init__(self, *argv):
    super().__init__(*argv[:3])
    args = list(argv)
    argc = len(args)
    try:
      self.className = args[3] if 3 < argc else None
      self.args = args[4:] if 4 < argc else None
    except:
      log(1, self.toJSON(), "Can't parse arguments", args)

    self.border = None
    self.__pdpy__ = self.__class__.__name__

class PdArray(PdObject):
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

class PdFont(Base):
  def __init__(self, face, size):
    # log(1,"PdFont", face, size)
    self.__pdpy__ = self.__class__.__name__
    self.face = self.num(face)
    self.name = PdFonts[self.face if self.face < len(PdFonts) else -1]
    self.size = self.num(size)

class IEMLabel(Base):
  def __init__(self, label, xoff, yoff, fface, fsize, lbcolor):
    self.__pdpy__ = self.__class__.__name__
    self.label = None if "empty" == label else label
    self.offset = Point(xoff, yoff)
    self.font = PdFont(fface, fsize)
    self.lbcolor = self.num(lbcolor)

class PdIEMGui(IEMLabel):
  def __init__(self, *argv):
    self.__pdpy__ = self.__class__.__name__
    self.id = argv[0]
    self.position = Point(*argv[1:3])
    self.className = argv[3]
    args = argv[4:]

    if "vu" in self.className:

      self.area = Size(*args[:2])
      self.receive = args[2]
      super().__init__(*args[3:8], args[9])
      self.bgcolor = self.num(args[8])
      self.scale= self.pdbool(args[10]) if 10 < len(args) else None
      self.flag = self.pdbool(args[11]) if 11 < len(args) else None
    
    elif "tgl" in self.className:

      self.size = self.num(args[0])
      self.init = self.pdbool(args[1])
      self.send = args[2] if args[2] != "empty" else None
      self.receive = args[3] if args[3] != "empty" else None
      super().__init__(*args[4:9], args[11])
      self.bgcolor = self.num(args[9])
      self.fgcolor = self.num(args[10])
      self.flag    = self.num(args[12])
      self.nonzero = self.num(args[13])

    elif "cnv" in self.className or "my_canvas" in self.className:

      self.size = self.num(args[0])
      self.area = Size(*args[1:3])
      if 12 < len(args):
        self.send = args[3] if args[3] != "empty" else None
        off = 0
      else:
        off = 1
      self.receive = args[4-off]  if args[4-off] != "empty" else None
      super().__init__(*args[5-off:10-off], args[11-off])
      self.bgcolor = self.num(args[10-off])
      self.flag    = self.num(args[12-off])

    elif "radio" in self.className or "rdb" in self.className:

      self.size   = self.num(args[0])
      self.flag   = self.num(args[1])
      self.init   = self.pdbool(args[2])
      self.number = self.num(args[3])
      self.send    = args[4] if args[4] != "empty" else None
      self.receive = args[5] if args[5] != "empty" else None
      super().__init__(*args[6:11], args[13])
      self.bgcolor = self.num(args[11])
      self.fgcolor = self.num(args[12])
      self.value   = self.num(args[14])

    elif "bng"    in self.className:
      self.size   = self.num(args[0])
      self.hold   = self.num(args[1])
      self.intrrpt= self.num(args[2])
      self.init   = self.pdbool(args[3])
      self.send    = args[4] if args[4] != "empty" else None
      self.receive = args[5] if args[5] != "empty" else None
      super().__init__(*args[6:11], args[13])
      self.bgcolor = self.num(args[11])
      self.fgcolor = self.num(args[12])

    elif "nbx"    in self.className:
      self.digit_width = self.num(args[0])
      self.height   = self.num(args[1])
      self.limits = Bounds(*args[2:4])
      self.log_flag = self.pdbool(args[4])
      self.init    = self.pdbool(args[5])
      self.send    = args[6] if args[6] != "empty" else None
      self.receive = args[7] if args[7] != "empty" else None
      super().__init__(*args[8:13], args[15])
      self.bgcolor = self.num(args[13])
      self.fgcolor = self.num(args[14])
      self.value = float(args[16])
      self.log_height = self.num(args[17])

    elif "sl" in self.className:
      self.area = Size(*args[:2])
      self.limits = Bounds(*args[2:4])
      self.log_flag = self.pdbool(args[4])
      self.init    = self.pdbool(args[5])
      self.send    = args[6] if args[6] != "empty" else None
      self.receive = args[7] if args[7] != "empty" else None
      super().__init__(*args[8:13], args[15])
      self.bgcolor = self.num(args[13])
      self.fgcolor = self.num(args[14])
      self.value = float(args[16])
      self.steady = self.num(args[17])

    else:
      log(1, "NEW IEM Gui", " ".join(argv))

class PdNativeGui(PdObj):
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
