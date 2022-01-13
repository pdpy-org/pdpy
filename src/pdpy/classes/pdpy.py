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
from .goparray import PdGOPArray
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
               xml=None):
    """ Initialize a PdPy object """

    self.patchname = name
    self.encoding = encoding
    self.__pdpy__ = self.__class__.__name__
    self.__canvas_idx__ = []
    self.__depth__ = 0

    CanvasBase.__init__(self, obj_idx=0)
    Base.__init__(self, json=json, xml=xml)
    
    if json is None and xml is None and pd_lines is not None:
      # parse the pd lines and populate the pdpy instance
      # account for pure data line endings and split into a list
      self.parse(pd_lines)
    
    if root:
      self.root = Canvas(json={'name':self.patchname,'isroot':True})
    
    # update the parent of all childs
    self.__jsontree__()
  
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
  
  def addRoot(self, argv=None, json=None):
    if argv is not None:
      self.root = Canvas(json={
              'name' : self.patchname,
              'vis' : 1,
              'id' : None, 
              'screen' : Point(x=argv[0], y=argv[1]),
              'dimension' : Size(w=argv[2], h=argv[3]), 
              'font' : int(argv[4]),
              'isroot' : True,
              '__p__' : self
      })
    elif json is not None:
      self.root = Canvas(json=json)

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

  def addCanvas(self, argv):
    """ Add a Canvas object from pure data syntax tokens
    
    Description:
    ------------
    This 
    """
    __canvas__ = self.__get_canvas__()
    canvas = Canvas(json={
            'name'   : argv[4],
            'vis'    : self.__num__(argv[5]),
            'id'     : self.__obj_idx__,
            'screen' : Point(x=argv[0], y=argv[1]), 
            'dimension' : Size(w=argv[2], h=argv[3]),
    })
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
    arr = PdGOPArray(json={
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

  def addConnection(self, pd_lines):
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
          if    7 == len(argv): last = self.addRoot(body)
          elif  8 == len(argv): last = self.addCanvas(body)
      elif "#A" == head[0]: #A -> text, savestate, or array  data
        super().__setdata__(last, Data(data=body, head=head[1]))
      else: #X -----------------> anything else is an "#X"
        if   "declare"    == head[1]: self.addDependencies(pd_lines=body)
        elif "coords"     == head[1]: self.addCoords(body)
        elif "connect"    == head[1]: self.addConnection(body) # edges
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
    
    s += f"{self.root.__pd__()}"

    if hasattr(self, 'dependencies'):
      s += f"{self.dependencies.__pd__()}"
    
    return super().__render__(s)

  def __xml__(self):
    """ Return the XML Element for this object """
    
    # root tag to which struct, 'root', and dependencies will be added
    x = super().__element__(scope=self, attrib={
      "encoding": self.encoding
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
    
    if hasattr(self, 'nodes'):
      nodes = super().__element__(tag='nodes')
      for e in getattr(self, 'nodes', []):
        self.__update_obj_map__(e)
        super().__subelement__(nodes, e.__xml__())
      super().__subelement__(root, nodes)

    if hasattr(self, 'comments'):
      comments = super().__element__(tag='comments')
      for e in getattr(self, 'comments', []):
        super().__subelement__(comments, e.__xml__())
      super().__subelement__(root, comments)

    if hasattr(self, 'coords'):
      super().__subelement__(root, self.coords.__xml__())
    
    if hasattr(self, 'edges'):
      edges = super().__element__(tag='edges')
      for e in getattr(self, 'edges', []):
        super().__subelement__(edges, e.__xml__(self.__obj_map__))
      super().__subelement__(root, edges)
    
    if hasattr(self, 'position'):
      super().__subelement__(root, self.position.__xml__())
    
    if hasattr(self, 'title'):
      super().__subelement__(root, 'title', text=self.title)
    
    return super().__tree__(x)
