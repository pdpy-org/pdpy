#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
""" PdPy file to Json-format file """

from ..patching.pdpy import PdPy
from ..connections.edge import Edge
from ..objects.obj import Obj
from ..objects.msg import Msg
from ..objects.comment import Comment
from ..primitives.point import Point
from ..memory.array import Array
from ..utilities.utils import log, tokenize
from ..utilities.regex import *

__all__ = [ 'PdPyParser' ]
LOG = 1

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
  def __init__(self, pdpy_lines, pddb, **kwargs):
    super().__init__(**kwargs)
    
    self.__pdpy__ = 'PdPy'
    self.__db__ = pddb
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
    self.__auto_patch__ = True
    self.__pdpy_lines__ = pdpy_lines

    self.parse()
  
  
  def parse(self):
    """ Parse the store pdpy file lines """

    for i, line in enumerate(self.__pdpy_lines__):
      self.__line_num__ = i
      log(LOG,"-"*30)
      log(LOG,repr(line))
      log(LOG,"-"*30)
      
      # Check for comments -----------------------------------------------------
      if is_ignored(line):
        continue
      
      # Check for root canvas -------------------------------------------------
      root, name = is_root(line)
      if root:
        self.root = self.addRoot()
        self.root.name = ' '.join(name) if bool(name) else self.patchname
        log(LOG,"Canvas Name:",self.root.name)
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
        cnv = self.addCanvas()
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
        __canvas__.__margin__.width += len(__canvas__.name)
        __canvas__.__cursor__.y += __canvas__.__box__.height
        log(LOG,"restored", __canvas__.name)
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
      
      log(LOG,"parsePdPyLine: Unparsed Lines:", repr(line))


  def objectConnector(self, source=None,sink=None, canvas=None):
    
    __canvas__ = self.__last_canvas__() if canvas is None else canvas
    #  canvas obj_index advances before this
    if source is None: source = __canvas__.__obj_idx__
    if sink is None: sink = __canvas__.__obj_idx__ + 1
    source_port = sink_port = 0
    log(LOG,"objectConnector", source, sink)
    pd_edge = (source, source_port, sink, sink_port)
    edge = Edge(pd_lines=pd_edge)
    __canvas__.edge(edge)    
    edge.__dumps__()

  def objectCreator(self, objClass, argv, root=False, canvas=None):
    
    __canvas__ = self.__last_canvas__() if canvas is None else canvas

    obj = None
    log(LOG,"objCreator",argv)

    word_length = len(argv) if isinstance(argv,str) else len(" ".join(argv))
    x, y = __canvas__.__cursor__.x, __canvas__.__cursor__.y
    if not root:
      __canvas__.__margin__.width += word_length
    else:
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

  def pdpyCreate(self, string):
    """ create pd stuff from pdpy lang 
    """
    log(LOG,"pdpyCreate",repr(string))
    
    # replace -> with loadbang ------------------------------------------------
    string = str(string).replace("->", "loadbang >")
    # string = string.replace("<-", "< loadbang")

    # tokenize ---------------------------------------------------------------
    self.__tokens__ = tokenize(string.strip())
    log(LOG,"Tokens are",*self.__tokens__)
    
    # ignore comments ---------------------------------------------------------
    c = ('//', '*', '/*', '*/') # comments
    sc = lambda c: str(self.__tokens__[0]).startswith(c) # check on first token
    if sum(filter(bool,map(sc, c))):
      # exit if the line is a comment
      return
    
    # check for connect all ---------------------------------------------------
    # if no connection token is presnt, then connect the entire lot
    k = ("<",">","->","<-") # konnections
    no = lambda token: token not in self.__tokens__
    self.__k__ = sum(filter(bool,map(no,k)))==len(k) and self.__auto_patch__
    log(LOG,"Connect All set to", self.__k__)

    # get the previous object index -------------------------------------------
    self.__prev__ = self.__last_canvas__().__obj_idx__
    
    # get the object map
    iso = lambda x : int(self.__db__.is_obj(x))
    self.__isomap__ = list(map(iso, self.__tokens__))
    log(LOG, "object map:", self.__isomap__)
    # get the iolets map
    hio = lambda x, y:self.__db__.has_iolets(x) if y else 0
    self.__hiomap__ = list(map(hio, self.__tokens__, self.__isomap__))
    log(LOG, "iolet  map:", self.__hiomap__)
    
    obj_count = sum(self.__isomap__)
    multiobj = obj_count > 1
    noobj = obj_count == 0    
    # arg_map = list(map(lambda x,y:self.arg_count(x) if y else None, self.__tokens__, self.__isomap__))

    if not multiobj:
      # single object
      log(LOG,"is single object", self.__tokens__)
      self.__last__ = self.parse_any(0, self.__tokens__[0])
      if hasattr(self,"__last__") and self.__last__ is not None:
        self.__last__.args = self.__tokens__[1:]
      if not self.__last___obj and hasattr(self.__hiomap__[0], 'outlets'):
        self.objectConnector()
      # if self.__k__:

    elif noobj:
      # no object
      log(LOG,"no objects", self.__tokens__)

    else:
      log(LOG,"is multi obj", multiobj, self.__tokens__)
      for i,t in enumerate(self.__tokens__):
        t = str(t).strip()
        """ Get argument count from pd databasw 
        """
        argc = self.__db__.arg_count(t)
        self.__store_args__ = argc is not None and self.__isomap__[i]
        
        if self.__store_args__: 
          self.__arg_number__ = argc
        log(LOG,t,"has",self.__arg_number__, "creation arguments.")
        
        
        """ Pd Argument Parser
        """
        log(LOG,"parse_arguments", i, t)
        log(LOG,"prev_obj_arg_num", self.__arg_number__)
        log(LOG, "is this an obj", self.__isomap__[i])
        if self.__arg_number__ and not self.__isomap__[i]:
          if hasattr(self,'__last__') and hasattr(self.__last__,'addargs'): 
            self.__last__.addargs([t])
            self.__arg_number__ -= 1
        
        """ Single-word messages
        """
        if '->' in t or '<-' in t or not self.__isomap__[i]:
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
          log(LOG,'symbol', t)
          self.__last__ = self.objectCreator(Array, ('array', 'define', '-k', t))
        
          """ Objects
          """
        elif self.__isomap__[i]: 
          log(LOG,"CREATING AN OBJECT", t)
          self.__last__ = self.objectCreator(Obj, (t))
        else:
          log(LOG,"UNKNOWN", t)
        
        """ Connections
        """
        obj = repr(t)
        
        if i >= len(self.__tokens__):
          log(LOG,"Is last object",t)
        
        elif not self.__isomap__[i]: 
          log(LOG,"Is not an object",t)
          # self.objectConnector(self.__prev__, self.__last__.id)

        elif not hasattr(self.__hiomap__[i], 'inlets'):
          log(LOG,"IOLETS",self.__hiomap__, t)

        if self.__k__: # and  i < len(self.__tokens__)-1:
          log(LOG,"Connect All!", obj) 
          if self.__prev__ != -1:
            self.objectConnector(self.__prev__, self.__last__.id)
          elif self.__last___obj:
            log(LOG,"__last___obj", obj, self.__last___obj) 
          else:
            self.objectConnector()
        else:

          if "->" == t: 
            log(LOG,"loadbang forward",obj)
          #   self.__last__ = self.objectCreator(Obj, ("loadbang"))
          #   self.objectConnector()
          #   return

          elif ">"  == t: 
            log(LOG,"forward",obj)
            if self.__store_cmd__:
              self.__store_cmd__ = False
              self.__last__ = self.objectCreator(Msg,(" ".join(self.__cmd__)))
              self.objectConnector(self.__prev__, self.__last__.id)
              self.__cmd__ = []
            else:
              self.objectConnector()
          
          elif "<-" == t: 
            log(LOG,"loadbang backwards",obj)
          #   self.__last__ = self.objectCreator(Obj, ("loadbang"))
          #   self.objectConnector(self.__last__.id,self.__prev__)
          #   return

          elif "<"  == t: 
            log(LOG,"backwards",obj)
            self.objectConnector(self.__obj_idx__-1,self.__obj_idx__)

