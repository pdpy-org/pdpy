#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
""" PdPy file to Json-format file """

import re

# from pdpy.parse.pdpy2json import is_ignored

from .pdpy import PdPy
from .canvas import Canvas
from .message import Msg
from .comment import Comment
from .connections import Edge
from .point import Point
from .obj import Obj
from .array import Array
from ..util.utils import log, printer, tokenize
from ..util.regex import *

__all__ = [ 'PdPyParser' ]


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
    self.__pdpy__ = 'PdPy'
    
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
    
    for i, line in enumerate(self.__lines__):
      self.__line_num__ = i
      # log(1,"-"*30)
      # log(1,repr(line))
      # log(1,"-"*30)
      
      # Check for comments -----------------------------------------------------
      if is_ignored(line):
        continue
      
      # Check for root canvas -------------------------------------------------
      root, name = is_root(line)
      if root:
        self.root = Canvas()
        self.root.name =  name if bool(name) else self.patchname
        if self.root.__cursor__.y > self.root.__margin__.height:
          self.root.__margin__.height = self.root.__cursor__.y
        self.__canvases__.append(self.root)
        continue
      
      # Check for canvas end --------------------------------------------------
      if is_root_end(line): 
        self.__canvases__.pop()
        continue
      
      # Check for subpatch ----------------------------------------------------
      subpatch, name = is_subpatch(line)
      if subpatch:
        __canvas__ = self.__get_canvas__()
        cnv = Canvas()
        cnv.id = self.__obj_idx__
        self.__canvas_idx__.append(__canvas__.add(cnv))
        
        if bool(name):
          cnv.name = " ".join(name).strip().replace(' ','\ ')

        self.__canvases__.append(cnv)
        continue
      
      # Check for subpatch end ------------------------------------------------
      if is_subpatch_end(line):
        piped = is_piped(line)
        # check first if pipe is present and pass an outlet
        if bool(piped):
          if 'outlet' not in self.__canvases__[-1].nodes:
            self.__prev__ = self.__last_canvas__().__obj_idx__
            self.__last__ = self.objectCreator(Obj, ('outlet'))
          self.objectConnector(self.__prev__,self.__last__.id)
        # restore the canvas
        __canvas__ = self.__last_canvas__()
        x, y = __canvas__.get_position()
        setattr(__canvas__, "position", Point(x, y))
        self.__last_canvas__().title = "pd " + __canvas__.name
        self.__depth__ -= 1
        if len(self.__canvas_idx__):
          self.__canvas_idx__.pop()
        __canvas__.grow_margins(len(__canvas__.name))
        __canvas__.__cursor__.y += __canvas__.__box__.height
        log(0,"restored", __canvas__.name)
        # check again and pass arguments to pipe through
        if bool(piped):
          string = " ".join(piped).strip()
          if bool(string):
            self.pdpyCreate(' '*len(self.__canvases__)*2 + string)
          # parsePdPyLine(' ' * len(canvases)*2 + " ".join(piped).strip())
          # patch.objectConnector()
        # clear the canvas out of the stack
        self.__canvases__.pop()

        continue
      
      # Check for pd-comments -------------------------------------------------
      comment = is_pdtext(line)
      if bool(comment) and isinstance(comment, list):
        self.objectCreator(Comment, (" ".join(comment).strip()), root=True)
        continue
      
      # Check for pd objects --------------------------------------------------
      objects = is_pdobj(line)
      if bool(objects) and isinstance(objects, list):
        self.pdpyCreate(" ".join(objects).strip())
      continue
      # log(1,"parsePdPyLine: Unparsed Lines:", repr(line))


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
      obj = Comment()
      obj.move(x, y)
      obj.addtext(argv)
      __canvas__.comment(obj)
    else:
      self.__obj_idx__ = __canvas__.grow() 
      if isinstance(argv, str): 
        pd_lines = [ self.__obj_idx__, x, y, argv ]
      else:
        pd_lines = [ self.__obj_idx__, x, y ] + argv
      obj = objClass(pd_lines=pd_lines)
      __canvas__.add(obj)

    return obj

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
    # if self.__connect_all__: log(1,"self.__connect_all__")

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
      log(1,"is single object", self.__tokens__)
      self.__last__ = self.parse_any(0, self.__tokens__[0])
      if hasattr(self,"__last__") and self.__last__ is not None:
        self.__last__.args = self.__tokens__[1:]
      if not self.__last___obj and hasattr(self.__iolet_map__[0], 'outlets'):
        self.objectConnector()
      return
      # if self.__connect_all__:
    elif noobj:
      # no object
      log(1,"no objects", self.__tokens__)
      return

    log(1,"is multi obj", multiobj, self.__tokens__)
    
    # i = 0
    # log(1,arg_map)
    # while i < len(self.__tokens__):

    #   self.__last__ = self.parse_any(i, self.__tokens__[i].strip())
    #   log(1,self.__last__, self.__tokens__[i])
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


    def get_args(i, t):
      """ Get argument count from pd databasw 
      """
      argc = self.arg_count(t)
      self.__store_args__ = argc is not None and self.__is_obj_map__[i]
      
      if self.__store_args__: 
        self.__arg_number__ = argc
      
      log(0,t,"has",self.__arg_number__, "creation arguments.")
    
    for i,t in enumerate(self.__tokens__):
      t = str(t).strip()
      get_args(i, t)
      
      """ Pd Argument Parser
      """
      # log(0,"parse_arguments", i, t)
      # log(0,"prev_obj_arg_num", self.__arg_number__)
      # log(0, "is this an obj", self.__is_obj_map__[i])
      if self.__arg_number__ and not self.__is_obj_map__[i]:
        if hasattr(self,'__last__') and hasattr(self.__last__,'addargs'): 
          self.__last__.addargs([t])
          self.__arg_number__ -= 1
      
      """ Single-word messages
      """
      if '->' in t or '<-' in t or not self.__is_obj_map__[i]:
        pass
      
      elif ((t.startswith("'") or t.startswith("\"")) and t.endswith("'") or t.endswith("\"")) or t.isnumeric():
        self.__last__ = self.objectCreator(Msg, t.replace("'",""))

        """ Messages
        """
      elif t.startswith("'") or t.startswith("\""):
        self.__msg__.append(t.replace("'",""))
        self.__store_msg__ = True
      
        """ Commands
        """
      elif 'sinesum' in t:
        self.__cmd__.append(t)
        self.__store_cmd__ = True

      elif self.__store_msg__:
        self.__msg__.append(t.replace("'",""))
        if t.endswith("'") or t.endswith("\""):
          self.__store_msg__ = False
          self.__last__ = self.objectCreator(Msg, (" ".join(self.__msg__)))
          self.__msg__ = []
      
        """ Symbols prepended with '\' become arrays, like sclang
        """
      elif t.startswith('\\'):
        t = t.replace('\\','') 
        log(0,'symbol', t)
        self.__last__ = self.objectCreator(Array, ('array', 'define', '-k', t))
      
        """ Objects
        """
      elif self.__is_obj_map__[i]: 
        # log(1,"CREATING AN OBJECT", t)
        self.__last__ = self.objectCreator(Obj, (t))
      else:
        log(0,"UNKNOWN", t)
      
      """ Connections
      """
      obj = repr(t)
      
      if i >= len(self.__tokens__):
        log(0,"Is last object",t)
      
      elif not self.__is_obj_map__[i]: 
        log(0,"Is not an object",t)
        # self.objectConnector(self.__prev__, self.__last__.id)

      elif not hasattr(self.__iolet_map__[i], 'inlets'):
        log(0,"IOLETS",self.__iolet_map__, t)
        # log(1,t, self.__iolet_map__[i])

      if self.__connect_all__: # and  i < len(self.__tokens__)-1:
        log(0,"Connect All!", obj) 
        if self.__prev__ != -1:
          self.objectConnector(self.__prev__, self.__last__.id)
        elif self.__last___obj:
          log(0,"__last___obj", obj, self.__last___obj) 
        else:
          self.objectConnector()
      else:

        # if "->" == t: 
        #   log(0,"loadbang forward",obj)
        #   self.__last__ = self.objectCreator(Obj, ("loadbang"))
        #   self.objectConnector()
        #   return

        if ">"  == t: 
          log(0,"forward",obj)
          if self.__store_cmd__:
            self.__store_cmd__ = False
            self.__last__ = self.objectCreator(Msg,(" ".join(self.__cmd__)))
            self.objectConnector(self.__prev__, self.__last__.id)
            self.__cmd__ = []
          else:
            self.objectConnector()
        
        # if "<-" == t: 
        #   log(0,"loadbang backwards",obj)
        #   self.__last__ = self.objectCreator(Obj, ("loadbang"))
        #   self.objectConnector(self.__last__.id,self.__prev__)
        #   return

        elif "<"  == t: 
          log(0,"backwards",obj)
          self.objectConnector(self.__obj_idx__-1,self.__obj_idx__)

  
  def objectConnector(self, source=None,sink=None, canvas=None):
    
    __canvas__ = self.__last_canvas__() if canvas is None else canvas
    #  canvas obj_index advances before this
    if source is None: source = __canvas__.__obj_idx__
    if sink is None: sink = __canvas__.__obj_idx__ + 1
    source_port = sink_port = 0
    log(0,"objectConnector", source, sink)
    pd_edge = (source, source_port, sink, sink_port)
    edge = Edge(pd=pd_edge)
    __canvas__.edge(edge)
    
    # edge.__dumps__()


 
