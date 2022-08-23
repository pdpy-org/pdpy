#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021-22 Fede Camara Halac
# **************************************************************************** #
""" 
PdPy
====
"""

from . import canvas, dependencies
from ..connections.edge import Edge
from ..core.base import Base
from ..core.canvasbase import CanvasBase
from ..primitives.point import Point
from ..primitives.size import Size
from ..primitives.coords import Coords
from ..iemgui.cnv import Cnv
from ..iemgui.toggle import Toggle
from ..iemgui.slider import Slider
from ..iemgui.radio import Radio
from ..iemgui.nbx import Nbx
from ..iemgui.bng import Bng
from ..iemgui.vu import Vu
from ..memory.struct import Struct
from ..memory.scalar import Scalar
from ..memory.graph import Graph
from ..memory.goparray import GOPArray
from ..memory.data import Data
from ..memory.array import Array
from ..objects.obj import Obj
from ..objects.msg import Msg
from ..objects.gui import Gui
from ..objects.comment import Comment
from ..utilities.utils import log
from ..utilities.default import *

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
    self.arrangement(5) # set the arrangement function
    # The following are used in the arrange function:
    # the horizontal step size for increments
    self.__hstep__ = 1.25 
    # the vertical step size for increments
    self.__vstep__ = 1

    CanvasBase.__init__(self, obj_idx=0)
    Base.__init__(self, json=json, xml=xml)
    
    if json is None and xml is None and pd_lines is not None:
      # parse the pd lines and populate the pdpy instance
      # account for pure data line endings and split into a list
      self.parse(pd_lines)
    
    if root:
      self.root = canvas.Canvas()
      self.root.isroot = True
      self.root.patchname = self.patchname
    
    if hasattr(self, 'root'):
      # update the parent of all childs
      self.__jsontree__()

    self.__set_pd_path__(pdpath)

  def __jsontree__(self):
    """ Spawn a json tree structure adding parents to every child """
    # log(0, f"{self.__class__.__name__}.__jsontree__()")
    setattr(self.root, '__p__', self)
    for x in getattr(self, 'structs', []):
      setattr(x, '__p__', self)
    self.__addparents__(self.root)

  def getTemplate(self, template_name):
    """ Get the template related to this object's Struct """
    for idx, s in enumerate(getattr(self, 'structs')):
      if template_name == getattr(s, 'name'):
        return idx, s
  
  def addStruct(self, pd_lines=None, json=None, xml=None):
    """ Add a Struct object from pure data syntax tokens """
    if not hasattr(self, 'structs'): 
      self.structs = []
    struct = Struct(pd_lines=pd_lines, json=json, xml=xml)
    struct.__parent__(self)
    self.structs.append(struct)  
  
  def addRoot(self, pd_lines=None, json=None, name=None):
    """ Add a root canvas object from pure data, json, or an empty canvas 

    Called by the :func:`parse` method as well as the :class:`pdpy.PdPyParser` class

    Return
    ------
    The root canvas object

    """
    if pd_lines is not None:
      self.root = canvas.Canvas()
      for x in [ ('screen', Point(x=pd_lines[0], y=pd_lines[1])),
                 ('dimension', Size(w=pd_lines[2], h=pd_lines[3])),
                 ('font', int(pd_lines[4])) ]: 
        setattr(self.root, x[0], x[1])
    
    elif json is not None:
      self.root = canvas.Canvas(json=json)
    
    else:
      self.root = canvas.Canvas()
    
    # Force these things to happen
    for x in [ ('__p__', self), 
               ('id', None), 
               ('isroot', True), 
               ('vis', 1), 
               ('name', name or self.patchname) ]:
      setattr(self.root, x[0], x[1])

    return self.root
  
  def addDependencies(self, **kwargs):
    """ Handle dependencies called with ``declare`` """
    if not hasattr(self,"dependencies"):
      self.dependencies = dependencies.Dependencies(**kwargs)
    else:
      self.dependencies.update(dependencies.Dependencies(**kwargs))

  def __last_canvas__(self):
    """ Returns the most recent canvas (from the nodes list)

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
    """ Return the last canvas taking depth and incrementing object index count """
    # __canvas__ = self.root if self.__depth__ == 0 else self.__last_canvas__()
    __canvas__ = self.__last_canvas__()
    self.__obj_idx__ = __canvas__.grow()
    self.__depth__ += 1
    return __canvas__

  def addCanvas(self, pd_lines=None, json=None):
    """ Add a canvas.Canvas object from pure data syntax tokens """
    from .canvas import Canvas
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
      canvas = canvas.Canvas(json=json)
    else:
      canvas = canvas.Canvas()
    
    if not hasattr(canvas, 'id'):
        setattr(canvas, 'id', self.__obj_idx__)
    
    self.__canvas_idx__.append(__canvas__.add(canvas))

    return canvas

  def addObj(self, argv):
    """ Add a Pd object from pure data syntax tokens """
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
    """ Add a Message object from pure data syntax tokens """
    # log(1,"msg", nodes)
    self.__obj_idx__ = self.__last_canvas__().grow()
    msg = Msg(pd_lines=[self.__obj_idx__]+argv)
    self.__last_canvas__().add(msg)
    return msg
  
  def addComment(self, argv):
    """ Add a Comment object from pure data syntax tokens """
    self.__last_canvas__().grow()
    # log(1,"COMMENT",argv)
    comment = Comment(pd_lines=argv)
    self.__last_canvas__().comment(comment)
    return comment

  def addNativeGui(self, className, argv):
    """ Add a Gui object from pure data syntax tokens """
    self.__obj_idx__ = self.__last_canvas__().grow()
    obj = Gui(pd_lines=[ className, self.__obj_idx__ ] + argv)
    self.__last_canvas__().add(obj)
    return obj

  def addGraph(self, argv):
    """ Add the ye-olde array ancestor from pure data syntax tokens """
    self.__obj_idx__ = self.__last_canvas__().grow()
    graph = Graph(pd_lines=[self.__obj_idx__, argv[0]] + argv[5:9] + argv[1:5])
    self.__last_canvas__().add(graph)
    return graph

  def addGOPArray(self, argv):
    """ Add a Graph-on-Parent Array object from pure data syntax tokens """
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
    """ Add a Scalar object from pure data syntax tokens """
    scalar = Scalar(struct=self.structs, pd_lines=pd_lines)
    self.__last_canvas__().add(scalar)
    return scalar

  def addEdge(self, pd_lines):
    """ Add a connection (Edge) object from pure data syntax tokens """
    self.__last_canvas__().edge(Edge(pd_lines=pd_lines))

  def addCoords(self, coords):
    """ Adds the Coords class to the canvas """
    setattr(self.__last_canvas__(), "coords", Coords(coords=coords))

  def restore(self, argv=None):
    """ Restore constructor called from :func:`parse` """
    # restored canvases also have borders
    # log(0,"RESTORE",argv)
    last = self.__last_canvas__()
    if argv is not None:
      setattr(last, 'position', Point(x=argv[0], y=argv[1]))
      setattr(last, 'title', ' '.join(argv[2:]))
    self.__depth__ -= 1
    if len(self.__canvas_idx__):
      self.__canvas_idx__.pop()
    return last
    
  def write(self, filename=None):
    """ Write out the pd file to disk """
    
    self.__arrange__(self)

    if filename is None:
      filename = self.patchname + '.pd'
    
    if '.pd' in filename:
      try:
        binbuf = self.__pd__()
      except Exception as e:
        log(3, e, "ERROR WITH BINBUF", self.patchname)
        raise Exception(e)
      with open(filename, 'w') as patchfile:
        patchfile.write(binbuf)
    
    elif '.json' in filename:
      with open(filename, 'w') as patchfile:
        patchfile.write(self.__json__())
  
  def parse(self, argvecs):
    """ Parse a list of Pd argument vectors (1) into this instance's scope

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
      """ Attempt to locate the ``pd`` executable """
      
      from sys import platform
      from pathlib import Path
      
      installed = False
      
      # print("Found ", platform, " platform.")
      
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
        # print("Locating pd...")
        apps = [p for p in sorted(pdpath.glob("Pd*.app"))]
        
        if len(apps) >= 1:
          appdir = apps[0]
        else:
          log(2, "Could not find pd in " + pdpath)

        pdbin = Path(appdir.as_posix() + bindir)
      
      if Path(pdbin).exists():
        # print("Found pd at: ", pdbin.as_posix())
        setattr(self, '__pdbin__', pdbin)
      else:
        log(2, "This pd binary does not exist: " + pdbin.as_posix())
    
  def run(self):
    """ Run Pd from the Pure Data binary """
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

  def arrangement(self, choice=-1):
    """ Sets the arranger function

    Parameters
    ----------
    choice: :class:`int`
      The choices are numbered starting at 0. If negative or not one of the available choices, it defaults to ``arrange1b``
    
    """

    if choice == 0: 
      # good, but fails on circular conections
      from ..utilities.arrange import arrange as _do_arrange
    elif choice == 1: 
      # this one fails
      from ..utilities.arrange1 import arrange1 as _do_arrange
    elif choice == 2: 
      # fails on dac~
      from ..utilities.arrange1a import arrange1a as _do_arrange
    elif choice == 3: 
      # max recursion depth error
      from ..utilities.arrange2 import arrange2 as _do_arrange
    elif choice == 5: 
      # max recursion depth error
      from ..extra.arranger import Arranger as _do_arrange
    else:
      # this one is nice (fails on dac~)
      from ..utilities.arrange1b import arrange1b as _do_arrange

    def _recurse_arrange(node):
      # in every child of ``node``, check if child is a parent
      for child in getattr(node, 'nodes', []):
        if hasattr(child, 'nodes'):
          # it is a parent, so recurse
          _recurse_arrange(child)
      # finally, arrange
      _do_arrange(node)
    
    def _begin_arrange(scope):
      if hasattr(scope, 'root'):
        _recurse_arrange(scope.root)

    self.__arrange__ = _begin_arrange
    
