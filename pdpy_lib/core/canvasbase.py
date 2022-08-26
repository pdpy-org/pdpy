#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021-22 Fede Camara Halac
# **************************************************************************** #
"""
Canvas Base
===========
"""

from ..connections.edge import Edge
from ..encoding.xmlbuilder import XmlBuilder


__all__ = [ 'CanvasBase' ]

class CanvasBase(XmlBuilder):
  """ Base class for a canvas
  
  This class is based by :class:`pdpy.PdPy` and :class:`pdpy.Canvas`
  
  """

  def __init__(self, obj_idx=0, isroot=False):
    """ Initialize the canvas base class """
    super().__init__()
    
    if isroot:
      self.isroot = isroot
    
    self.__obj_idx__ = obj_idx

    # This is a dictionary with 
    # - the node indices as keys, and 
    # - the last self.__depth_list__ index as values
    self.__obj_map__ = {}
    
  def __update_obj_map__(self, x):
    """ Update the object map with the current object

    This method updates the object map with the current object. This is meant
    to keep track of the objects in the current canvas, so we can connect
    them later with their respective edges.
    """
    # If the node has an ID, get it and use it to update the object map
    if hasattr(x, "id"):
      # increment the index by one
      self.__obj_idx__ += 1
      # add the node to the map so that 
      # key is the id and value is the index
      self.__obj_map__.update({
        int(getattr(x,'id')) : self.__obj_idx__
      })
  
  def __edges__(self, s):
    for x in getattr(self, 'edges', []):
      s += x.__pd__(self.__obj_map__)
    return s

  def __nodes__(self, s):
    for x in getattr(self, 'nodes', []):
      self.__update_obj_map__(x)
      s += x.__pd__()
    return s

  def __comments__(self, s):
    for x in getattr(self, 'comments', []):
      s += x.__pd__()
    return s

  def __coords__(self, s):
    if hasattr(self, 'coords'):
      s += self.coords.__pd__()
    return s

  def __restore__(self, s, isgraph=False):
    if hasattr(self, 'position'):
      s += "#X restore " + self.position.__pd__()
      if hasattr(self, 'title'):
        s += " " + self.title
      if isgraph:
        s += " graph"
      s += self.__end__
    return s
  
  def __render__(self, s, isroot=False, isgraph=False):
    s = self.__nodes__(s)
    s = self.__comments__(s)
    if isroot:
      # argh, this order is swapped for the root canvas
      s = self.__coords__(s)
      s = self.__edges__(s)
    else:
      s = self.__edges__(s)
      s = self.__coords__(s)
    s = self.__restore__(s, isgraph=isgraph)
    return s
  
  def __xml_nodes__(self, parent):
    if hasattr(self, 'nodes'):
      nodes = super().__element__(tag='nodes')
      for e in getattr(self, 'nodes', []):
        self.__update_obj_map__(e)
        super().__subelement__(nodes, e.__xml__())
      super().__subelement__(parent, nodes)

  def __xml_comments__(self, parent):
    if hasattr(self, 'comments'):
      comments = super().__element__(tag='comments')
      for e in getattr(self, 'comments', []):
        super().__subelement__(comments, e.__xml__())
      super().__subelement__(parent, comments)

  def __xml_edges__(self, parent):
    if hasattr(self, 'edges'):
      edges = super().__element__(tag='edges')
      for e in getattr(self, 'edges', []):
        super().__subelement__(edges, e.__xml__(self.__obj_map__))
      super().__subelement__(parent, edges)

  def edge(self, edge):
    """ Append a pure data connection (edge)

    This method creates and/or appends a pure data connection as an `Edge`.
    See `Edge` to see how connections are handled.

    Return
    ------
    None
    """
    if not hasattr(self, 'edges'): 
      self.edges = []
    super().__parent__(self, edge)
    self.edges.append(edge.connect())
    # log(1,"Edge",edge.__dict__)
  
  def disconnect(self, *argv):
    """ Attempt to disconnect the objects """
    cnv = self.__last_canvas__() if hasattr(self, '__last_canvas__') else self
    
    # return if there are no edges
    if not len(cnv.edges): return
    
    try:
      argv = sorted(argv, key = lambda x:x.id)
    except ValueError as e:
      # skip uncreated objects
      print("Object not created on the canvas: missing id")
      print(e)
    
    # loop through the arguments
    for arg in argv:
      # skip uncreated objects
      # if not hasattr(arg, 'id'): continue
      # second loop through the edges
      for i, edge in enumerate(sorted(cnv.edges, key = lambda x:x.source.id)):
        
        # if the object id matches any, remove it
        if arg.id in (edge.source.id, edge.sink.id):
          cnv.edges.pop(i)
          print("Disconnected", arg.id)
          break

      # # second loop through the edges
      # i = 0
      # while len(self.edges):
      #   # if the object id matches any, remove it
      #   if arg.id in (self.edges[i].source.id, self.edges[i].sink.id):
          
      #     self.edges.pop(self.edges.index(i))
      #   i += 1


  def connect(self, *argv):
    """ Attempt to autoconnect the objects together """
    cnv = self.__last_canvas__() if hasattr(self, '__last_canvas__') else self

    length = len(argv)
    
    stepsize = 1
    maxlen = length - 1
    
    # utility routine 
    def _connect(*argv):
      # print(argv)
      e = Edge(pd_lines=argv)
      cnv.edge(e)

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

  def comment(self, comment):
    """ Append a pure data comment

    This method creates and/or appends a pure data comment. 

    Return
    ------
    None
    """
    if not hasattr(self, 'comments'): 
      self.comments = []
    self.comments.append(comment)

  def create(self, *anything):
    """ Create an object, message, comment, or any other pd object """
    cnv = self.__last_canvas__() if hasattr(self, '__last_canvas__') else self
    from ..objects.comment import Comment # for the create method
    for a in anything:
      self.__obj_idx__ = self.grow()
      if isinstance(a, Comment):
        cnv.comment(a)
      else:
        a.id = cnv.add(a)
      a.__parent__(parent=cnv)
    return self

  def createComment(self, *anything):
    """ Helper to create comments """
    from ..objects.comment import Comment
    comments = list(map(lambda x:Comment(x), anything))
    self.create(*comments)
    return comments

  def createCanvas(self, **kwargs):
    """ Create a subpatch """
    from ..patching.canvas import Canvas
    canvas = Canvas(**kwargs)
    if not hasattr(canvas, 'title'):
      canvas.title = "pd " + canvas.name
    last_canvas = self.__last_canvas__()
    canvas.id = self.__obj_idx__
    canvas.__parent__(parent=last_canvas)
    self.__canvas_idx__.append(last_canvas.add(canvas))

    return canvas

  def __set_array_name__(self, array):
    """ Sets the name of the array incrementing the array name index """
    if not hasattr(array, 'name'):
      self.__arr_idx__ += 1
      array.name = "array" + str(self.__arr_idx__)

  def createArray(self, **kwargs):
    """ Create a GOP Array construction on the canvas """
    from ..memory.array import Array
    
    array = Array(**kwargs)
    
    self.__set_array_name__(array)
    
    canvas = self.__last_canvas__()

    array.__parent__(parent=canvas)
    
    self.create(array)
    
    return array

  def createGOPArray(self, **kwargs):
    """ Create a GOP Array construction on the canvas """
    from ..patching.canvas import Canvas
    from ..primitives.coords import Coords
    from ..memory.goparray import GOPArray
    
    array = GOPArray(**kwargs)

    self.__set_array_name__(array)

    canvas = Canvas()
    canvas.name = self.__d__.name
    canvas.vis = 0
    
    canvas.dimension.set_height(self.__d__.arrdimen['height'])
    array.id = canvas.add(array)
    array.__parent__(parent=canvas)

    setattr(canvas, 'coords', Coords(gop=1))
    setattr(canvas, 'isgraph', True)

    if hasattr(canvas, 'title'):
      delattr(canvas, 'title')
    
    self.create(canvas)
    
    return array

  def grow(self):
    """ Increments the canvas object index by 1 """
    self.__obj_idx__ += 1
    return self.__obj_idx__
  
  def add(self, node):
    """ Add (append) a Node to this canvas ``nodes``

    This method creates and/or appends a node to an internal array ``nodes``.
    Each node is a Pure Data object that is neither a comment nor a connection

    Return
    ------
    
    :class:`int`
      The position (index) of the most recently added node

    """
    if not hasattr(self, 'nodes'): 
      self.nodes = []
    self.nodes.append(node)
    return len(self.nodes) - 1
