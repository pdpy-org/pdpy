#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" PdPy file to Json-format file """

import re

from pdpy.parse.pdpy2json import is_ignored

from ..classes.pdpy import PdPy
from ..classes.canvas import Canvas
from ..classes.classes import Comment, Edge, PdArray, PdMessage, PdObject, Point
from ..util.utils import log, printer, tokenize

__all__ = [ "PdPyParser" ]

class PdPyParser(PdPy):
  """ Reads the lines from a .pdpy file pointer `fp` and populates a `PdPy` obj
    
    Returns
    -------
    A PdPy patch objects

    Input
    -----
    1. `.pdpy` file pointer `fp`
    2. `pddb` is a json file holding a pure data object database

    """
  def __init__(self, fp, pddb, **kwargs):
    super().__init__(**kwargs)
    
    self.__pddb__ = pddb
    self.__lines__ = fp.readlines()
    # self.__lines__ = fp.read()

    self.__msg__ = [] # to store a message
    self.__cmd__ = [] # to store a command ('sinesum', etc)
    self.__store_msg__ = False
    self.__store_cmd__ = False
    self.__arg_number__ = 0 # to store arguments
    self.__store_args__ = False
    self.__arguments__ = []
    self.__last___obj = False
    self.__canvases__ = []
    self.__last__ = None #  the las object     
    
    for i, s in enumerate(self.__lines__):
      self.__line_num__ = i
      self.parsePdPyLine(s)
    # self.dumps()


  def arg_count(self, q):
    """ Query the database for object number of creation self.__arguments__
    """
    for x in self.__pddb__:
      if len(x.classes):
        for c in x.classes:
          if hasattr(c,'attributes') and hasattr(c.attributes,'arguments') and hasattr(c.attributes.arguments,'name') and q == c.attributes.arguments.name:
            return len(c.attributes.arguments.args)

  def is_obj(self, q):
    """ Query the database to check if it is a pd object or not
    """
    if '->' in q or '<-' in q: return True
    if not (">" in q or "<" in q or q.startswith("\\") or "'" in q):
      for x in self.__pddb__:
        if len(x.classes):
          for c in x.classes:
            if hasattr(c,'attributes') and hasattr(c.attributes,'arguments'):
              if (hasattr(c.attributes.arguments,'name') and q == c.attributes.arguments.name) or q == c.attributes.arguments: 
                return True
    return False

  def has_iolets(self, q):
    """ Query the database to check if the pd object has iolets, return obj
    """
    if '->' in q or '<-' in q: 
      return self.has_iolets('loadbang')
    if not (">" in q or "<" in q or q.startswith("\\") or "'" in q):
      for x in self.__pddb__:
        if len(x.classes):
          for c in x.classes:
            if hasattr(c,'attributes') and hasattr(c.attributes,'iolets'):
              if (hasattr(c.attributes.arguments,'name') and q == c.attributes.arguments.name): 
                return c.attributes.iolets
    return False

  def get_args(self, i, t):
      """ Get argument count from pd databasw 
      """
      argc = self.arg_count(t)
      self.__store_args__ = argc is not None and self.__is_obj_map__[i]
      
      if self.__store_args__: 
        self.__arg_number__ = argc
      
      log(0,t,"has",self.__arg_number__, "creation arguments.")
  
  def parse_arguments(self, i, t):
    """ Pd Argument Parser
    """
    # log(0,"parse_arguments", i, t)
    # log(0,"prev_obj_arg_num", self.__arg_number__)
    # log(0, "is this an obj", self.__is_obj_map__[i])
    if self.__arg_number__ and not self.__is_obj_map__[i]:
      if hasattr(self,'__last__') and hasattr(self.__last__,'addargs'): 
        self.__last__.addargs([t])
        self.__arg_number__ -= 1

  def make_connections(self, i, t):
    """ Connections
    """
    obj = repr(t)
    
    if i >= len(self.__tokens__):
      log(0,"Is last object",t)
      return
    
    if not self.__is_obj_map__[i]: 
      log(0,"Is not an object",t)
      return

    if not hasattr(self.__iolet_map__[i], 'inlets'):
      log(0,"IOLETS",self.__iolet_map__, t)
      # log(1,t, self.__iolet_map__[i])
      return



    if self.__connect_all__: # and  i < len(self.__tokens__)-1:
      log(0,"Connect All!", obj) 
      if self.__prev__ != -1:
        self.objectConnector(self.__prev__, self.__last__.id)
      elif self.__last___obj:
        return
      else:
        self.objectConnector()
    else:

      # if "->" == t: 
      #   log(0,"loadbang forward",obj)
      #   self.__last__ = self.objectCreator(PdObject, ("loadbang"))
      #   self.objectConnector()
      #   return

      if ">"  == t: 
        log(0,"forward",obj)
        if self.__store_cmd__:
          self.__store_cmd__ = False
          self.__last__ = self.objectCreator(PdMessage,(" ".join(self.__cmd__)))
          self.objectConnector(self.__prev__, self.__last__.id)
          self.__cmd__ = []
          return
        else:
          self.objectConnector()
          return
      
      # if "<-" == t: 
      #   log(0,"loadbang backwards",obj)
      #   self.__last__ = self.objectCreator(PdObject, ("loadbang"))
      #   self.objectConnector(self.__last__.id,self.__prev__)
      #   return

      if "<"  == t: 
        log(0,"backwards",obj)
        self.objectConnector(self.__obj_idx__-1,self.__obj_idx__)
        return

  def parse_any(self, i, t):
    """ Single-word messages
    """
    if '->' in t or '<-' in t or not self.__is_obj_map__[i]: 
      return

    if ((t.startswith("'") or t.startswith("\"")) and t.endswith("'") or t.endswith("\"")) or t.isnumeric():
      return self.objectCreator(PdMessage, t.replace("'",""))

    """ Messages
    """
    if t.startswith("'") or t.startswith("\""):
      self.__msg__.append(t.replace("'",""))
      self.__store_msg__ = True
      return
    
    """ Commands
    """
    if 'sinesum' in t:
      self.__cmd__.append(t)
      self.__store_cmd__ = True
      return

    if self.__store_msg__:
      self.__msg__.append(t.replace("'",""))
      if t.endswith("'") or t.endswith("\""):
        self.__store_msg__ = False
        self.__last__ = self.objectCreator(PdMessage, (" ".join(self.__msg__)))
        self.__msg__ = []
        return self.__last__
      return
    
    """ Symbols prepended with '\' become arrays, like sclang
    """
    if t.startswith('\\'):
      t = t.replace('\\','') 
      log(0,'symbol', t)
      return self.objectCreator(PdArray, ('array', 'define', '-k', t))
    
    """ Objects
    """
    if self.__is_obj_map__[i]: 
      # print("CREATING AN OBJECT", t)
      return self.objectCreator(PdObject, (t))


  def pdpyCreate(self, string, autoconnect=True):
    """ create pd stuff from pdpy lang 
    """
    
    string = string.replace("->", "loadbang >")
    # string = string.replace("<-", "< loadbang")
    log(0,"pdpyCreate",repr(string))

    self.__tokens__ = tokenize(string.strip())
    log(0,"Tokens are",self.__tokens__)
    
    

    # if no connection token is presnt, then connect the entire lot
    self.__connect_all__ = ( ">" not in self.__tokens__ and "<" not in self.__tokens__ and "->" not in self.__tokens__ and "<-" not in self.__tokens__ ) and autoconnect
    # if self.__connect_all__: print("self.__connect_all__")

    # ignore comments
    if self.__tokens__[0].startswith("//") or self.__tokens__[0].startswith("/*") or self.__tokens__[0].startswith(" *") or self.__tokens__[0].startswith("*/"): 
      return

    self.__prev__ = self.__last_canvas__().__obj_idx__
    
    
    self.__is_obj_map__=list(map(lambda x:int(self.is_obj(x)), self.__tokens__))
    self.__iolet_map__=list(map(lambda x, y:self.has_iolets(x) if y else 0, self.__tokens__, self.__is_obj_map__))
    log(0,"object map:", self.__is_obj_map__)
    log(0, "iolet map:", self.__iolet_map__)

    
    obj_count = sum(self.__is_obj_map__)
    multiobj = obj_count > 1
    noobj = obj_count == 0    
    # arg_map = list(map(lambda x,y:self.arg_count(x) if y else None, self.__tokens__, self.__is_obj_map__))


    if not multiobj:
      # single object
      print("is single object", self.__tokens__)
      self.__last__ = self.parse_any(0, self.__tokens__[0])
      if hasattr(self,"__last__") and self.__last__ is not None:
        self.__last__.args = self.__tokens__[1:]
      if not self.__last___obj and hasattr(self.__iolet_map__[0], 'outlets'):
        self.objectConnector()
      return
      # if self.__connect_all__:
    elif noobj:
      # no object
      print("no objects", self.__tokens__)
      return

    print("is multi obj", multiobj, self.__tokens__)
    
    # i = 0
    # print(arg_map)
    # while i < len(self.__tokens__):

    #   self.__last__ = self.parse_any(i, self.__tokens__[i].strip())
    #   print(self.__last__, self.__tokens__[i])
    #   if arg_map[i] and self.__last__ is not None:
    #     arg = arg_map[i]
    #     if hasattr(self.__last__,'addargs'):
    #       self.__last__.addargs(self.__tokens__[i:i+arg])
    #     while arg:
    #       i += 1
    #       arg -= 1
    #   self.make_connections(self.__tokens__[i].strip())
    #   i += 1
      # get_args(i, t)
      # parse_self.__arguments__(t)
      # parse_any(i, t)


    for i,t in enumerate(self.__tokens__):
      t = t.strip()
      self.get_args(i, t)
      self.parse_arguments(i, t)
      self.__last__ = self.parse_any(i, t)
      self.make_connections(i, t)
      # log(0,"self.__last__",self.__last__.id,"self.__prev__",self.__prev__)
      # log(0,t, f"{'Is an' if self.__is_obj_map__[i] else 'Is not an'} Object")
      # print(f"object {t} has {argc} argument{'s' if argc>1 else ''}")
    # that's it

  def pdpyComment(self, string, border=None):
    log(0,"pdpyComment",string)
    obj = self.objectCreator(Comment, (string), root=True)
    
    if border is not None:
      obj.border=border

  def pdpyRoot(self, name=None):
    log(0,"createRoot",name)
    name = self.patchname.replace(".pd","") if name is None else name
    self.root = Canvas(name=name)
    len_name = self.root.get_char_dim()
    border = len_name if len_name > 60 else None
    self.pdpyComment("*" * len_name, border=border)
    self.pdpyComment(f"* {name} *",  border=border)
    self.pdpyComment("*" * len_name, border=border)

    if self.root.__cursor__.y > self.root.__margin__.height:
      self.root.__margin__.height = self.root.__cursor__.y
    
    return self.root

  def pdpyCanvas(self, **kwargs):
    """ Create a Canvas object from parameters
    """
    log(0,"pdpyCanvas",kwargs)
    __canvas__ = self.__get_canvas__()
    canvas = Canvas(id = self.__obj_idx__, **kwargs)
    self.__canvas_idx__.append(__canvas__.add(canvas))
    return canvas

  def pdpyRestore(self):
    """ Restore constructor from pdpy files
    """
    __canvas__ = self.__last_canvas__()
    x, y = __canvas__.get_position()
    setattr(__canvas__, "position", Point(x, y))
    self.__last_canvas__().title = "pd " + __canvas__.name
    self.__depth__ -= 1
    if len(self.__canvas_idx__):
      self.__canvas_idx__.pop()
    __canvas__.grow_margins(len(__canvas__.name))
    __canvas__.__cursor__.y += __canvas__.__box__.height
    log(0,"pdpyRestore", __canvas__.name)
    return __canvas__  
  
  def objectCreator(self, objClass, argv, root=False, canvas=None):
    
    __canvas__ = self.__last_canvas__() if canvas is None else canvas

    obj = None
    log(0,"objCreator",argv)

    word_length = len(argv) if isinstance(argv,str) else len(" ".join(argv))
    if not root:
      x, y = __canvas__.get_position()
      __canvas__.grow_margins(word_length)
    else:
      x, y = __canvas__.get_position()
      __canvas__.__cursor__.y += __canvas__.__box__.height
    
    if objClass is Comment:
      obj = Comment(x, y, argv)
      __canvas__.comment(obj)
    else:
      self.__obj_idx__ = __canvas__.grow() 
      if isinstance(argv, str): 
        obj = objClass(self.__obj_idx__, x, y, argv)
        __canvas__.add(obj)
      else:
        obj = objClass(self.__obj_idx__, x, y, *argv)
        __canvas__.add(obj)

    return obj

  def objectConnector(self, source=None,sink=None, canvas=None):
    
    __canvas__ = self.__last_canvas__() if canvas is None else canvas
    #  canvas obj_index advances before this
    if source is None: source = __canvas__.__obj_idx__
    if sink is None: sink = __canvas__.__obj_idx__ + 1
    source_port = sink_port = 0
    log(0,"objectConnector", source, sink)
    edge = Edge(
     source, source_port,
     sink, sink_port
    )
    __canvas__.edge(edge)
    
    # edge.dumps()

  @printer
  def is_ignored(self, s): 
    """ Ignore out-of-patch comments
    """
    return bool(re.search(r"^/\*.*$", s)    or 
                re.search(r"^\s\*.*$", s) or 
                re.search(r"^\*/$", s)    or 
                re.search(r"^[\s]*//", s) or 
                re.search(r"^\n", s))

  @printer
  def is_root(self, s):
    """ Root canvas opening parens
    """
    if re.search(r"^\(.*$",s):
      name = re.findall(r"^\(#(.*)$", s)
      if bool(name):
        log(0,"NAME", name)
        root = self.pdpyRoot(name=" ".join(name).strip())
      else:
        root = self.pdpyRoot()
      self.__canvases__.append(root)
      return True

  @printer
  def is_root_end(self, s):
    """ Root canvas closing parens (ignores root canvas restore)
    """
    if re.search(r"^\).*$",s):
      self.__canvases__.pop()
      return True
  
  @printer
  def is_subpatch(self, s):
    """ Create Pd Canvases
    """
    if re.search(r"^\s+\(.*$",s):
      name = re.findall(r"^\s+\(#(.*)$",s)
      if bool(name):
        cnv = self.pdpyCanvas(name=" ".join(name).strip().replace(' ','\ '))
      else:
        cnv = self.pdpyCanvas()
      self.__canvases__.append(cnv)
      return True

  @printer
  def is_subpatch_end(self, s):
    """ Ends a subpatch (calls restore and pipes args after parens)
    """
    if re.search(r"^\s+\).*$",s):
      piped = re.findall(r"^\s+\)(.*)$",s)
      # check first if pipe is present and pass an outlet
      if bool(piped):
        if 'outlet' not in self.__canvases__[-1].nodes:
          self.__prev__ = self.__last_canvas__().__obj_idx__
          self.__last__ = self.objectCreator(PdObject, ('outlet'))
        self.objectConnector(self.__prev__,self.__last__.id)
      # restore the canvas
      self.pdpyRestore()
      # check again and pass arguments to pipe through
      if bool(piped):
        string = " ".join(piped).strip()
        # string = 
        if bool(string):
          self.pdpyCreate(' '*len(self.__canvases__)*2 + string)
        # parsePdPyLine(' ' * len(canvases)*2 + " ".join(piped).strip())
        # patch.objectConnector()
      # clear the canvas out of the stack
      self.__canvases__.pop()
      return True
  
  @printer
  def is_pdtext(self, s):
    """ Adds a pure data in-patch comment to the canvas
    """
    if re.search(r"^\s+[#+].+$", s):
      comment = re.findall(r"^\s+[#+](.+)$", s) 
      if bool(comment):
        self.pdpyComment(" ".join(comment).strip())
      return True

  @printer
  def is_pdobj(self, s):
    """ Any object creator on the pd canvas
    """
    if re.search(r"^\s+[\*\w\d\\\-%\+\/].+$", s): 
      objects = re.findall(r"^\s+([\*\w\d\\\-%\+\/].+)$", s) 
      if bool(objects):
        print("pdobj",objects)
        self.pdpyCreate(" ".join(objects).strip())
      return True

  def parsePdPyLine(self, s):
    """ PdPy line parsing dispatcher
    """
    # print("-"*30)
    # print(repr(s))
    # print("-"*30)
    if self.is_ignored(s): return
    if self.is_root(s): return
    if self.is_root_end(s): return
    if self.is_subpatch(s): return
    if self.is_subpatch_end(s): return
    if self.is_pdtext(s): return    
    if self.is_pdobj(s): return
    # log(1,"parsePdPyLine: Unparsed Lines:", repr(s))
  
  






  # def create(self, obj):
  #   """ Create a Pd obj, msg, text, and graph from pdpy class definitions

  #   Description
  #   -----------
  #   Allowed `pdpy` class definitions are:
  #     - `PdObject`    : `PdObject.__doc__`
  #     - `PdArray`     : `PdArray.__doc__`
  #     - `PdIEMGui`    : `PdIEMGui.__doc__`
  #     - `PdNativeGui` : `PdNativeGui.__doc__` 
  #     - `Graph`       : `Graph.__doc__`
  #     - `PdMessage`   : `PdMessage.__doc__`
  #     - `Comment`     : `Comment.__doc__`
  #   """
  #   self.__obj_idx__ = self.__last_canvas__().grow()
  #   self.__last_canvas__().add(obj)
   













        # signal / nonsignal objects
        # elif "~" in t:
        
          # if   t in internals.signal.math:           print("s math obj",obj)
          # elif t in internals.signal.fourier:        print("s fourier obj",obj)
          # elif t in internals.signal.filters:        print("s filter obj",obj)
          # elif t in internals.signal.flow:           print("s flow obj",obj)
          # elif t in internals.signal.delays:         print("s delays obj",obj)
          # elif t in internals.signal.route:          print("s route obj",obj)
          # elif t in internals.signal.generators:     print("s gen obj",obj)
          # elif t in internals.signal.system:         print("s sys obj",obj)
          # elif t in internals.signal.control_to_sig: print("s c2s obj",obj)
          # elif t in internals.signal.array:          print("s tab obj",obj)
          # elif t in internals.signal.block:          print("s block obj",obj)
          # elif t in internals.signal.analysis:       print("s analysis obj",obj)
          # else:
          #   log(1, "Unknown signal object", obj)
          
          # self.objectCreator(PdObject, (t))
          
        
        # else:

          # if   t in internals.interface.midi:     
          #   print("i midi obj", obj)
          # self.__last__ = self.objectCreator(PdObject, (t))
          # elif t in internals.interface.keyboard: 
          #   print("i key obj", obj)
          #   self.objectCreator(PdObject, (t))
          # elif t in internals.interface.system:   
          #   print("i sys obj", obj)
          #   self.objectCreator(PdObject, (t))
          # elif t in internals.interface.gui:      
          #   print("i gui obj", obj)
            # self.objectCreator(PdIEMGui, (t))

          # elif t in internals.operators.math:       
          #   print("o math obj", obj)
          #   self.objectCreator(PdObject, (t))
          # elif t in internals.operators.binary:     
          #   print("o bin obj", obj)
          #   self.objectCreator(PdObject, (t))
          # elif t in internals.operators.comparison: 
          #   print("o comp obj", obj)
          #   self.objectCreator(PdObject, (t))

          # elif t in internals.data.array: 
          #   print("d array obj", obj)
          #   self.objectCreator(PdArray, (t))
          # elif t in internals.data.struct: 
          #   print("d struct obj", obj)
          # elif t in internals.data.text: 
          #   print("d text obj", obj)
          #   self.objectCreator(PdArray, (t))
          # elif t in internals.data.other: 
          #   print("d other obj", obj)
          #   self.objectCreator(PdObject, (t))
    
          # elif t in internals.parsing.list: 
          #   print("p list obj", obj)
          #   self.objectCreator(PdObject, (t))
          # elif t in internals.parsing.stream: 
          #   print("p stream obj", obj)
          #   self.objectCreator(PdObject, (t))
          # elif t in internals.parsing.format: 
          #   print("p format obj", obj)
          #   self.objectCreator(PdObject, (t))
    
          # elif t in internals.control.flow: 
          #   print("c flow obj", obj)
          #   self.objectCreator(PdObject, (t))
          # elif t in internals.control.network: 
          #   print("c net obj", obj)
          #   self.objectCreator(PdObject, (t))
          # elif t in internals.control.math: 
          #   print("c math obj", obj)
          #   self.objectCreator(PdObject, (t))
          # elif t in internals.control.time: 
          #   print("c time obj", obj)
          #   self.objectCreator(PdObject, (t))
          # elif t in internals.control.generators: 
          #   print("c gen obj", obj)
          #   self.objectCreator(PdObject, (t))

          # elif t in internals.nonobj: 
          #   print("nonobj", obj)
          # elif t in internals.obsolete: 
          #   print("obsolete", obj)
          # elif t in internals.extra: 
          #   print("extra", obj)
          
          # else:

          # if checknum(t): 
            # print("number", self.num(t))
            # self.objectCreator(PdMessage, (self.num(t)))
          
          # else:
            # log(2,"Unable to create object", obj)
        
        
        # remove self.__arguments__ once we have passed them through
        # self.__arguments__ = []
  
