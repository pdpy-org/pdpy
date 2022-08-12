#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" PdPy class definition """

from .base import Base
from .canvasbase import CanvasBase
from .default import *
from .point import Point
from .size import Size
from .coords import Coords
from .cnv import Cnv
from .toggle import Toggle
from .slider import Slider
from .radio import Radio
from .nbx import Nbx
from .bng import Bng
from .vu import Vu
from .canvas import Canvas
from .struct import Struct
from .scalar import Scalar
from .graph import Graph
from .goparray import GOPArray
from .data import Data
from .obj import Obj
from .array import Array
from .gui import Gui
from .message import Msg
from .dependencies import Dependencies
from .comment import Comment
from .connections import Edge
from ..util.utils import log

__all__ = [ 'PdPy' ]

class PdPy(CanvasBase, Base):
  
  def __init__(self, 
               name=None,
               encoding='utf-8',
               root=False,
               pd_lines=None,
               json=None,
               xml=None,
               pdpath=None):
    """ Initialize a PdPy object """
    
    self.patchname = Base.__sane_name__(self, name)
    self.encoding = encoding
    self.__pdpy__ = self.__class__.__name__
    self.__canvas_idx__ = []
    self.__depth__ = 0
    self.__max_w__ = 0
    self.__max_h__ = 0
    self.__soring_alg__ = 3

    if self.__soring_alg__ == 0: # good, but fails on circular conections
      from ..util.arrange import arrange
    elif self.__soring_alg__ == 1: # this one fails
      from ..util.arrange1 import arrange1 as arrange
    elif self.__soring_alg__ == 2: # fails on dac~
      from ..util.arrange1a import arrange1a as arrange
    elif self.__soring_alg__ == 3: # this one is nice (fails on dac~)
      from ..util.arrange1b import arrange1b as arrange
    elif self.__soring_alg__ == 4: # max recursion depth error
      from ..util.arrange2 import arrange2 as arrange
    else:
      arrange = lambda x:x
    

    # The following are used in the arrange function:
    # the horizontal step size for increments
    self.__hstep__ = 1.25 
    # the vertical step size for increments
    self.__vstep__ = 1
    
    self.arrange = arrange
    

    CanvasBase.__init__(self, obj_idx=0)
    Base.__init__(self, json=json, xml=xml)
    
    if json is None and xml is None and pd_lines is not None:
      # parse the pd lines and populate the pdpy instance
      # account for pure data line endings and split into a list
      self.parse(pd_lines)
    
    if root:
      self.root = Canvas()
      self.root.isroot = True
      self.root.patchname = self.patchname
    
    if hasattr(self, 'root'):
      # update the parent of all childs
      self.__jsontree__()

    self.__set_pd_path__(pdpath)


  def __jsontree__(self):
    # log(0, f"{self.__class__.__name__}.__jsontree__()")
    setattr(self.root, '__p__', self)
    for x in getattr(self, 'structs', []):
      setattr(x, '__p__', self)
    self.__addparents__(self.root)

  def getTemplate(self, template_name):
    for idx, s in enumerate(getattr(self, 'structs')):
      if template_name == getattr(s, 'name'):
        return idx, s
  
  def addStruct(self, pd_lines=None, json=None, xml=None):
    if not hasattr(self, 'structs'): 
      self.structs = []
    struct = Struct(pd_lines=pd_lines, json=json, xml=xml)
    struct.__parent__(self)
    self.structs.append(struct)  
  
  def addRoot(self, pd_lines=None, json=None, name=None):
    """ Add a root canvas object from pure data, json, or an empty canvas 
    
    Description:
    ------------
    Called by the parse() method as well as the PdPyParser class

    Returns:
    --------
    The root canvas object

    """
    if pd_lines is not None:
      self.root = Canvas()
      for x in [ ('screen', Point(x=pd_lines[0], y=pd_lines[1])),
                 ('dimension', Size(w=pd_lines[2], h=pd_lines[3])),
                 ('font', int(pd_lines[4])) ]: 
        setattr(self.root, x[0], x[1])
    
    elif json is not None:
      self.root = Canvas(json=json)
    
    else:
      self.root = Canvas()
    
    # Force these things to happen
    for x in [ ('__p__', self), 
               ('id', None), 
               ('isroot', True), 
               ('vis', 1), 
               ('name', name or self.patchname) ]:
      setattr(self.root, x[0], x[1])

    return self.root
  
  def addDependencies(self, **kwargs):
    """ handle embedded declarations
    """
    if not hasattr(self,"dependencies"):
      self.dependencies = Dependencies(**kwargs)
    else:
      self.dependencies.update(Dependencies(**kwargs))

  def __last_canvas__(self):
    """ Returns the most recent canvas (from the nodes list)

    Description
    -----------
    1. Start at the root canvas
    2. Do `__depth__` amount of iterations (0 depth will return `self.root`)
    3. Get the `canvas_node_index` by indexing `__canvas_idx__` with `__depth__`
    4. Return the canvas located at that `canvas_node_index`
    """
    
    __canvas__ = self.root
    for idx in range(self.__depth__):
      canvas_node_index = self.__canvas_idx__[idx]
      __canvas__ = __canvas__.nodes[canvas_node_index]
  
    return __canvas__
  
  def __get_canvas__(self):
    """ Return the last canvas taking depth and incrementing object index count
    """
    # __canvas__ = self.root if self.__depth__ == 0 else self.__last_canvas__()
    __canvas__ = self.__last_canvas__()
    self.__obj_idx__ = __canvas__.grow()
    self.__depth__ += 1
    return __canvas__

  def addCanvas(self, pd_lines=None, json=None):
    """ Add a Canvas object from pure data syntax tokens
    
    Description:
    ------------
    This 
    """
    __canvas__ = self.__get_canvas__()
    if pd_lines is not None:
      canvas = Canvas(json={
              'name'   : pd_lines[4],
              'vis'    : self.__num__(pd_lines[5]),
              'id'     : self.__obj_idx__,
              'screen' : Point(x=pd_lines[0], y=pd_lines[1]), 
              'dimension' : Size(w=pd_lines[2], h=pd_lines[3]),
      })
    elif json is not None:
      canvas = Canvas(json=json)
    else:
      canvas = Canvas()
    
    if not hasattr(canvas, 'id'):
        setattr(canvas, 'id', self.__obj_idx__)
    
    self.__canvas_idx__.append(__canvas__.add(canvas))

    return canvas

  def addObj(self, argv):
    """ Add a Pd object from pure data syntax tokens
    """
    # log(1,"addOBJ", argv)
    self.__obj_idx__ = self.__last_canvas__().grow()
    if 2 == len(argv):
      # an empty object
      obj = Obj(pd_lines = [self.__obj_idx__] + argv)
      self.__last_canvas__().add(obj)
    else:
      # protect against argv not being a list
      if not isinstance(argv, list):
        argv = [argv]
      # text-group object
      if "text" == argv[2]:
        obj = Array(pd_lines = [self.__obj_idx__] + argv)
        self.__last_canvas__().add(obj)
      # array-group object
      elif "array" == argv[2]:
        obj = Array(pd_lines = [self.__obj_idx__] + argv)
        self.__last_canvas__().add(obj)
      # scalar-define object
      elif "scalar" == argv[2]:
        obj = Array(pd_lines = [self.__obj_idx__] + argv)
        self.__last_canvas__().add(obj)
      # file-define object
      elif "file" == argv[2]:
        obj = Array(pd_lines = [self.__obj_idx__] + argv)
        self.__last_canvas__().add(obj)
      # IEMGUI-group object
      elif argv[2] in IEMGuiNames:
        # log(1, "NODES:", argv)
        if "vu" in argv[2]:
          obj = Vu(pd_lines = [self.__obj_idx__] + argv)
        elif "tgl" in argv[2]:
          obj = Toggle(pd_lines = [self.__obj_idx__] + argv)
        elif "cnv" in argv[2] or "my_canvas" in argv[2]:
          obj = Cnv(pd_lines = [self.__obj_idx__] + argv)
        elif "radio" in argv[2] or "rdb" in argv[2]:
          obj = Radio(pd_lines = [self.__obj_idx__] + argv)
        elif "bng"    in argv[2]:
          obj = Bng(pd_lines = [self.__obj_idx__] + argv)
        elif "nbx"    in argv[2]:
          obj = Nbx(pd_lines = [self.__obj_idx__] + argv)
        elif "sl" in argv[2]:
          obj = Slider(pd_lines = [self.__obj_idx__] + argv)
        else:
          raise ValueError("Unknown class name: {}".format(self.className))
      
        self.__last_canvas__().add(obj)
      # TODO: make special cases for data structures
      # - drawing instructions
      else:
        obj = Obj(pd_lines = [self.__obj_idx__] + argv)
        self.__last_canvas__().add(obj)
    return obj
  
  def addMsg(self, argv):
    # log(1,"msg", nodes)
    self.__obj_idx__ = self.__last_canvas__().grow()
    msg = Msg(pd_lines=[self.__obj_idx__]+argv)
    self.__last_canvas__().add(msg)
    return msg
  
  def addComment(self, argv):
    self.__last_canvas__().grow()
    # log(1,"COMMENT",argv)
    comment = Comment(pd_lines=argv)
    self.__last_canvas__().comment(comment)
    return comment

  def addNativeGui(self, className, argv):
    self.__obj_idx__ = self.__last_canvas__().grow()
    obj = Gui(pd_lines=[ className, self.__obj_idx__ ] + argv)
    self.__last_canvas__().add(obj)
    return obj

  def addGraph(self, argv):
    """ The ye-olde array ancestor
    """
    self.__obj_idx__ = self.__last_canvas__().grow()
    graph = Graph(pd_lines=[self.__obj_idx__, argv[0]] + argv[5:9] + argv[1:5])
    self.__last_canvas__().add(graph)
    return graph

  def addGOPArray(self, argv):
    # log(1,"addGOPArray", argv)
    arr = GOPArray(json={
      'name' : argv[0],
      'length' : argv[1],
      'type' : argv[2],
      'flag' : argv[3],
      'className' : "goparray"
    }, cls='array')
    self.__last_canvas__().add(arr)
    return arr
  
  def addScalar(self, pd_lines):
    scalar = Scalar(struct=self.structs, pd_lines=pd_lines)
    self.__last_canvas__().add(scalar)
    return scalar

  def addEdge(self, pd_lines):
    self.__last_canvas__().edge(Edge(pd_lines=pd_lines))

  def addCoords(self, coords):
    """ the coords constructor
    """
    setattr(self.__last_canvas__(), "coords", Coords(coords=coords))

  def restore(self, argv=None):
    """ Restore constructor
    """
    # restored canvases also have borders
    # log(0,"RESTORE",argv)
    last = self.__last_canvas__()
    if argv is not None:
      setattr(last, 'position', Point(x=argv[0], y=argv[1]))
      setattr(self.__last_canvas__(), 'title', ' '.join(argv[2:]))
    self.__depth__ -= 1
    if len(self.__canvas_idx__):
      self.__canvas_idx__.pop()
    return last

  def create(self, *anything):
    """ Create an object, message, comment, or any other pd object """
    for a in anything:
      canvas = self.__last_canvas__()
      self.__obj_idx__ = canvas.grow()
      a.id = canvas.add(a)
      a.__parent__(parent=canvas)
    return self

  def createArray(self, array):
    """ Create a GOP Array construction on the canvas """
    canvas = Canvas()
    canvas.name = self.__d__.name
    canvas.vis = 0
    
    canvas.dimension.set_height(self.__d__.arrdimen['height'])
    array.id = canvas.add(array)
    array.__parent__(parent=canvas)

    setattr(canvas, 'coords', Coords(gop=1))
    setattr(canvas, 'isgraph', True)
    
    self.create(canvas)
    
    return self
    
  def write(self, filename=None):
    """ Write out the pd file to disk """
    
    self.arrange(self)

    if filename is None:
      filename = self.patchname + '.pd'
    
    if '.pd' in filename:
      try:
        binbuf = self.__pd__()
      except Exception as e:
        print(e, "ERROR WITH BINBUF", self.patchname)
        raise Exception(e)
      with open(filename, 'w') as patchfile:
        patchfile.write(binbuf)
    
    elif '.json' in filename:
      with open(filename, 'w') as patchfile:
        patchfile.write(self.__json__())
  
  def connect(self, *argv):
    """ Attempt to autoconnect the objects together """
    length = len(argv)
    
    stepsize = 1
    maxlen = length - 1
    
    # utility routine 
    def _connect(*argv):
      e = Edge(pd_lines=argv)
      self.__last_canvas__().edge(e)

    for i in range(0, maxlen, stepsize):
      src = argv[i] # the source
      snk = argv[i+1] # the sink
      # check if we are lists
      srclist = isinstance(src, list)
      snklist = isinstance(snk, list)
      # neither is a list
      if not srclist and not snklist:
        _connect(src.id, 0, snk.id, 0)
      # only sink is a list (connect sequentially to multiple inlets)
      elif not srclist and snklist:
        for i in range(1,len(snk)):
          _connect(src.id, 0, snk[0].id, snk[i])
      # only source is a list (connect sequentially from multiple outlets)
      elif srclist and not snklist:
        for i in range(1,len(src)):
          _connect(src[0].id, src[i], snk.id, 0)  
      # both are lists (limit to minimum iolets between source and sink), so
      # connect([source, 0, 1, 2], [sink, 1, 2]) gives
      # #X connect source.id 0 sink.id 1
      # #X connect source.id 1 sink.id 2 
      elif srclist and snklist:
        for i in range(1,min(len(src),len(snk))):
          _connect(src[0].id, src[i], snk[0].id, snk[i])

  def parse(self, argvecs):
    """ Parse a list of Pd argument vectors (1) into this instance's scope

    Description:
    ------------
    This method populates the current class with appropriate calls to 
    individual classes refered to by parsing the argument vector `argv`.

    (1) A pure data argument vector is a list containing a tokenized version
    of the pure data file line (binbuf), starting with '#' and ending with ';'.
    The tokens are split by spaces, ignoring escaped chars. The special char
    ',' is handled before calling this method.

    """
    # log(1,f'Parsing {len(argvecs)} pd_lines')
    # print(type(argvecs))
    store_graph = False
    last = None

    for argv in argvecs:
      # log(1, "argv:", argv)
      head = argv[:2] 
      body = argv[2:]
      # log(1, "head:", head, "body:", body)
      
      
      if "#N"   == head[0]: #N -> either structs or canvases
        if "struct" == head[1]: self.addStruct(body) # struct element
        else: # check if we are root or canvas node
          if    7 == len(argv): last = self.addRoot(pd_lines=body)
          elif  8 == len(argv): last = self.addCanvas(pd_lines=body)
      elif "#A" == head[0]: #A -> text, savestate, or array  data
        super().__setdata__(last, Data(data=body, head=head[1]))
      else: #X -----------------> anything else is an "#X"
        if   "declare"    == head[1]: self.addDependencies(pd_lines=body)
        elif "coords"     == head[1]: self.addCoords(body)
        elif "connect"    == head[1]: self.addEdge(body) # edges
        elif "floatatom"  == head[1]: last = self.addNativeGui(head[1], body)
        elif "symbolatom" == head[1]: last = self.addNativeGui(head[1], body)
        elif "listbox"    == head[1]: last = self.addNativeGui(head[1], body)
        elif "scalar"     == head[1]: last = self.addScalar(body)
        elif "text"       == head[1]: last = self.addComment(body)
        elif "msg"        == head[1]: last = self.addMsg(body)
        elif "obj"        == head[1]: last = self.addObj(body)
        elif "pop"        == head[1]: store_graph = False # pop the array old
        elif "f"          == head[1]: setattr(last, "border", int(body[0]))
        elif "graph"      == head[1]: 
          last = self.addGraph(body)
          store_graph = True
        elif "array"      == head[1]: # fill; check if we are in a graph
          if store_graph: last.addArray(head[1], *body)
          else: last = self.addGOPArray(body)
        elif "restore"    == head[1]: #TODO do something to graph restore...?
          if "graph" == body[-1]: last = self.restore(body)
          else:                   last = self.restore(body)
        else: log(1,"What is this?", argv, self.patchname)

  def __pd__(self):
    """ Unparse this instance's scope into a list of pure data argument vectors

    Description:
    ------------
    This method returns a list of pure data argument vectors (1) from this 
    class' scope.

    """
    s = ''
    for x in getattr(self,'structs', []):
      s += x.__pd__()
    
    s += self.root.__pd__()

    if hasattr(self, 'dependencies'):
      s += self.dependencies.__pd__()
    
    return super().__render__(s)

  def __xml__(self):
    """ Return the XML Element for this object """
    
    # root tag to which struct, 'root', and dependencies will be added
    x = super().__element__(scope=self, attrib={
      "encoding": self.encoding, 
      "xml:space": "preserve"
      })
    
    if hasattr(self, 'structs'):
      structs = super().__element__(tag="structs")
      for e in getattr(self,'structs', []):
        super().__subelement__(structs, e.__xml__())
      super().__subelement__(x, structs)

    if hasattr(self, 'dependencies'):
      super().__subelement__(x, self.dependencies.__xml__())
    
    # make the 'root' tag to which all other elements will be added
    root = self.root.__xml__(tag='root')
    # add the 'root' tag to the xml root
    super().__subelement__(x, root)
    
    super().__xml_nodes__(root)
    super().__xml_comments__(root)

    if hasattr(self, 'coords'):
      super().__subelement__(root, self.coords.__xml__())
    
    super().__xml_edges__(root)

    if hasattr(self, 'position'):
      super().__subelement__(root, self.position.__xml__())
    
    if hasattr(self, 'title'):
      super().__subelement__(root, 'title', text=self.title)
    
    return super().__tree__(x)

  def __set_pd_path__(self, path_to_pd):
      """ Attempt to locate the ``pd`` executable
      """
      
      from sys import platform
      from pathlib import Path
      
      installed = False
      
      print("Found ", platform, " platform.")
      
      if "darwin" in platform: # macos
        pdpath = Path("/Applications")
        bindir = "/Contents/Resources/bin/pd"
      elif "win" in platform: # windoz
        pdpath = Path("C:/Program Files (x86)")
        bindir = "/usr/bin/pd"
      else: # asume pd is out there
        installed = True
        pdbin = Path("/")
      
      if path_to_pd is not None:
        pdpath = Path(path_to_pd)

      if installed:
        pdbin += "pd"
      else:
        print("Locating pd...")
        apps = [p for p in sorted(pdpath.glob("Pd*.app"))]
        
        if len(apps) >= 1:
          appdir = apps[0]
        else:
          raise Exception("Could not find pd in " + pdpath)

        pdbin = Path(appdir.as_posix() + bindir)
      
      if Path(pdbin).exists():
        print("Found pd at: ", pdbin.as_posix())
        setattr(self, '__pdbin__', pdbin)
      else:
        raise Exception("This pd binary does not exist: " + pdbin.as_posix())
    
  def run(self):
    from subprocess import run as __run__
    if not hasattr(self, 'patchname'):
      raise Exception("No patchname found")
    if not hasattr(self, '__pdbin__'):
      raise Exception("Pd binary not set.")
    command = [
      self.__pdbin__.as_posix(),
      "-open",
      self.patchname+".pd",
    ]
    __run__(" ".join(command), shell=True, check=True)

  def __enter__(self):
    return self
  
  def __exit__(self, ctx_type, ctx_value, ctx_traceback):
    self.write()
    