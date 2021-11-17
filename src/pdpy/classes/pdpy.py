#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" PdPy class definition """

from ..util.utils import log
from .base import Base
from .classes import *
from .pddata import PdData
from .pdobject import PdObject
from .pdarray import PdArray
from .gui import PdNativeGui
from .message import PdMessage
from .canvas import Canvas
from .dependencies import Dependencies
from .comment import Comment
from .connections import Edge
from .data_structures import *
from .default import *
from .iemgui import *
from ..parse.json2pd import JsonToPd

__all__ = [ "PdPy" ]

class PdPy(Base):
  
  def __init__(self, 
               name=None,
               encoding='utf-8',
               root=False,
               pd_lines=None,
               json_dict=None,
               xml_object=None):

    """ Initialize a PdPy object """

    super().__init__()

    self.patchname = name
    self.encoding = encoding
    self.__pdpy__ = self.__class__.__name__
    self.__obj_idx__ = 0
    self.__canvas_idx__ = []
    self.__depth__ = 0

    if pd_lines is not None:
      # parse the pd lines and populate the pdpy instance
      # account for pure data line endings and split into a list
      self.parse(pd_lines)
    
    elif json_dict is not None:
      # populate this class scope from the json_dict
      super().__populate__(self, json_dict)
    
    elif xml_object is not None:
      log(2,"XML INPUT NOT IMPLEMENTED")
    
    else:
      log(1,f"{self.__pdpy__}: Neither json_dict nor xml_object nor pd_lines keyword arguments were passed")
    
    if root:
      self.root = Canvas(json_dict={'name':self.patchname,'isroot':True})

  
  def getTemplate(self, template_name):
    if hasattr(self, 'struct'):
      for idx, s in enumerate(getattr(self, 'struct')):
        if template_name == getattr(s, 'name'):
          return idx, s
  
  def addStruct(self, argv, source='pd'):
    if not hasattr(self, 'struct'): 
      self.struct = []
    if source == 'xml':
      # log(1, "addStruct", argv)
      self.struct.append(Struct(argv, source=source))
    else:
      self.struct.append(Struct(*argv, source=source))
    
    self.struct[-1].parent(self)
  
  def addRoot(self, argv):
    self.root = Canvas(json_dict={
            'name' : self.patchname,
            'vis' : 1,
            'id' : None, 
            'screen' : Point(x=argv[0], y=argv[1]),
            'dimension' : Size(w=argv[2], h=argv[3]), 
            'font' : int(argv[4]),
            'isroot' : True
    })
    return self.root
  
  def addDependencies(self, argv):
    """ handle embedded declarations
    """
    if not hasattr(self,"dependencies"):
      self.dependencies = Dependencies(*argv)
    else:
      self.dependencies.update(Dependencies(*argv))

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
    canvas = Canvas(json_dict={
            'name'   : argv[4],
            'vis'    : argv[5],
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
      obj = PdObject(pd_lines = [self.__obj_idx__] + argv)
      self.__last_canvas__().add(obj)
    else:
      # protect against argv not being a list
      if not isinstance(argv, list):
        argv = [argv]
      # text-group object
      if "text" == argv[2]:
        obj = PdArray(pd_lines = [self.__obj_idx__] + argv)
        self.__last_canvas__().add(obj)
      # array-group object
      elif "array" == argv[2]:
        obj = PdArray(pd_lines = [self.__obj_idx__] + argv)
        self.__last_canvas__().add(obj)
      # IEMGUI-group object
      elif argv[2] in IEMGuiNames:
        # log(1, "NODES:", argv)
        obj = PdIEMGui(pd_lines=[self.__obj_idx__] + argv)
        self.__last_canvas__().add(obj)
      # TODO: make special cases for data structures
      # - drawing instructions
      else:
        obj = PdObject(pd_lines = [self.__obj_idx__] + argv)
        self.__last_canvas__().add(obj)
    return obj
  
  def addMsg(self, argv):
    # log(1,"msg", nodes)
    self.__obj_idx__ = self.__last_canvas__().grow()
    msg = PdMessage(pd_lines=[self.__obj_idx__]+argv)
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
    obj = PdNativeGui(className=className, pd_lines=[self.__obj_idx__]+argv)
    self.__last_canvas__().add(obj)
    return obj

  def addGraph(self, argv):
    """ The ye-olde array ancestor
    """
    self.__obj_idx__ = self.__last_canvas__().grow()
    graph = Graph(pd_lines=[self.__obj_idx__, argv[0]] + argv[4:9] + argv[1:5])
    self.__last_canvas__().add(graph)
    return graph

  def addGOPArray(self, argv):
    # log(1,"addGOPArray", argv)
    arr = PdType(json_dict={
      'name' : argv[0],
      'size' : argv[1],
      'type' : argv[2],
      'flag' : argv[3],
      'className' : "goparray"
    })
    self.__last_canvas__().add(arr)
    return arr
  
  def addScalar(self, argv):
    scalar = Scalar(struct=self.struct, pd_lines=argv)
    self.__last_canvas__().add(scalar)
    return scalar

  def addConnection(self, argv):
    self.__last_canvas__().edge(Edge(pd=argv))

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
      setattr(last, "position", Point(x=argv[0], y=argv[1]))
      self.__last_canvas__().title = ' '.join(argv[2:])
    self.__depth__ -= 1
    if len(self.__canvas_idx__):
      self.__canvas_idx__.pop()
    return last

  def parse(self, argvecs):
    """ Parse a list of pure data argument vectors (1) into this class' scope

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
        if   "set"        in head[1]:
          setattr(last, 'data', PdData(body, dtype=str, char=';',head=head[1]))
        elif "saved"      in head[1]:
          setattr(last, 'data', PdData(body, dtype=str,head=head[1]))
        else:
          setattr(last, 'data', PdData(body))
      else: #X -----------------> anything else is an "#X"
        if   "declare"    == head[1]: self.addDependencies(body)
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
          if store_graph: last.addArray(head[1], body[1])
          else: last = self.addGOPArray(body)
        elif "restore"    == head[1]: #TODO do something to graph restore...?
          if "graph" == body[-1]: last = self.restore(body)
          else:                   last = self.restore(body)
        else: log(1,"What is this?", argv, self.patchname)
  
  def __pd__(self):
    """ Unparse this class' scope into a list of pure data argument vectors

    Description:
    ------------
    This method returns a list of pure data argument vectors (1) from this 
    class' scope.

    """
    # log(1, "Unparsing")
    # return list(map(lambda x:x.__pd__(), self.root))
    
    # __pd__ recursion order:    

    # struct
    # root
    # - dependencies
    # nodes
    # comments
    # coords
    # edges
    # restore

    return JsonToPd(self).getpd()
