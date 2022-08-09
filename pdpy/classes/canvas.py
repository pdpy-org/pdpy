#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Canvas Class Definition """

from .base import Base
from .canvasbase import CanvasBase
from .point import Point
from .size import Size

__all__ = [ 'Canvas' ]
class Canvas(CanvasBase, Base):
  """ A Pure Data 'canvas' or 'subpatch' represented as a `pdpy` object

  Description:
  ------------
  This class holds the pure data subpach/canvas properties 
  as defined in the pure data text file.
  
  `Canvas` has some base properties inherited from the super class
  `Properties`. Besides basic properties, the `Canvas` class takes 
  `#X connect`, `#X coords`, and `#X restore` into its own namespace, 
  as well as the pure data nodes that are created within the context 
  of a subpatch/canvas window. 

  Attributes:
  ----------
  - `__pdpy__` (`str`) PdPy className (`self.__class__.__name__`)
  - `name`     (`str`) The canvas name on parent ('(subpatch)')
  - `vis`      (`bool`) Flag to tell if canvas should be visible or not (False)
  - `gop`      (`bool`) Flag to tell if canvas should Graph on Parent (False)
  - `coords`   (`Coords`) Obj holding coordinates necessary for GOP (None)  
  - `position` (`Point`) X-Y pair defining where the pd box is graphed (None)  
  - `title`    (`str`) Name to display on the canvas window title bar (None)
  - `border`   (`int`) Position of the object's box right border  (None)
  - `id`       (`int`) Identifier number for connections (None)
  - `__obj_idx__`  (`int`) Number of objects currently on this canvas (-1)

  The basic properties come
  from the pure data file representation: `#N canvas 0 22 450 300 12;`

  Attributes:
  -----------
  `screen` (`Point`) x-y pair of the top-left window corner on the screen (0,22)
  `dimension` (`Size`) window width and height dimensions (450, 300)
  `font` (`int`) window font size (12)
  `__pdpy__` (`str`) PdPy className (`self.__class__.__name__`)
  
  """
  def __init__(self, json=None):

    CanvasBase.__init__(self, obj_idx=-1)
    Base.__init__(self, pdtype='N', cls='canvas')
    self.__pdpy__ = self.__class__.__name__
    
    if json is not None:
      super().__populate__(self, json)
    else:
      self.screen = Point(x=0, y=22)
      self.dimension = Size(w=450, h=300)
      self.font = 12
      self.vis = 0
      self.name = self.__d__.name
    
    if hasattr(self, 'isroot'):
      self.isroot = self.__pdbool__(self.isroot)
    
    if hasattr(self, 'font'):
      self.font = self.__num__(self.font)
      self.__pad__ = Size(w=self.font, h=self.font)
      self.__cursor_init__ = Point(x=self.font, y=self.font)
      self.__cursor__ = Point(x=self.font, y=self.font)
      self.__box__ = Size(w=int(self.font * 1.25), h=int(self.font * 2))
      self.__margin__ = Size(w=self.font, h=self.font)

  def grow(self):
    """ Increments the canvas object index by 1
    """
    self.__obj_idx__ += 1
    return self.__obj_idx__
  
  def add(self, node):
    """ Add (append) a Node to this canvas `nodes`

    Description:
    ------------
    This method creates and/or appends a 'node' to an internal array `nodes`.
    Each node is a Pure Data object that is neither a comment nor a connection

    Returns:
    --------
    The position (index) of the most recently added node

    """
    if not hasattr(self, 'nodes'): 
      self.nodes = []
    self.nodes.append(node)
    return len(self.nodes) - 1

  def edge(self, edge):
    """ Append a pure data connection (edge)

    Description:
    ------------
    This method creates and/or appends a pure data connection as an `Edge`.
    See `Edge` to see how connections are handled.

    Return:
    -------
    None
    """
    if not hasattr(self, 'edges'): 
      self.edges = []
    super().__parent__(self, edge)
    self.edges.append(edge.connect())
    # log(1,"Edge",edge.__dict__)

  def comment(self, comment):
    """ Append a pure data comment

    Description:
    ------------
    This method creates and/or appends a pure data comment. 

    Return:
    -------
    None
    """
    if not hasattr(self, 'comments'): 
      self.comments = []
    self.comments.append(comment)

  def update_cursor(self, w_step=12, h_step=12):
    """ Fill objects from top to bottom until we reach bottom
    (used to be get_position)
    """
    print("Object Size:", w_step, h_step)
    mod_x = self.__cursor__.x // self.dimension.width
    mod_y = self.__cursor__.y // self.dimension.height

    # def _print():
    #   print(self.__cursor__.x, self.__cursor__.y, mod_x, mod_y)

    # if mod_x > 1 and mod_y > 1:
    #   print("out of bounds --------------------")
    # # if cursor is out of bounds, grow downwards...
    #   # reset x, 
    #   # resize the canvas to be twice as tall as before
    #   # and make y be the bottom most position
    #   self.__cursor__.x = self.__cursor_init__.x
    #   self.__cursor__.y += self.dimension.height
    #   self.__cursor__.y += self.__pad__.height
    #   return

    # if mod_x < 1 and mod_y > 1:
    #   print("surpassed y", mod_y)
    #   # reset y and increment x position
    #   self.dimension.set_height(self.dimension.height * 2)
    #   self.__cursor__.y = self.__cursor_init__.y + h_step
    #   self.__cursor__.x += w_step
    #   return

    # if mod_x > 1 and mod_y < 1:
    #   print("surpassed x")
    #   # reset x and increment y position
    #   self.dimension.set_width(self.dimension.width * 2)
    #   self.__cursor__.y += self.dimension.height * (1+mod_y)
    #   self.__cursor__.x = self.__cursor_init__.x
    #   return 

    # grow downwards
    self.__cursor__.y += h_step

  def get_char_dim(self):
    return int(self.dimension.width / self.font * 1.55)

  def get(self, id):
    if hasattr(self, 'nodes'):
      for node in self.nodes:
        if node.id == id:
          return node
    else:
      return None

  def __pd__(self):
    """ Pure Data representation of the canvas """

    # the canvas line
    s = super().__pd__()

    # print("Screen:",self.screen.__pd__())
    # print("Dimension:",self.dimension.__pd__())
    # print("Name:",self.name)
    # print("Font:",self.font)
    # print("Vis:",self.vis)
    # print("End:",repr(self.__end__))

    s += " " + self.screen.__pd__() + " " + self.dimension.__pd__()
    
    isroot = getattr(self, 'isroot', False)
    isgraph = getattr(self, 'isgraph', False)

    if isroot:
      # root canvas only reports font
      s += " " + str(self.font)
    else:
      # non-root canvases, report their name and their vis status
      s += " " + self.name + " " + str(1 if self.vis else 0)
    
    # end the line so we can continue appending to `s`
    s += self.__end__
    
    s = super().__render__(s, isroot=isroot, isgraph=isgraph)
    
    # the border, only if not root
    if hasattr(self, 'border') and (not isroot):
      s += "#X f " + str(self.border)
      s += self.__end__

    return s


  def __xml__(self, tag=None):
    """ Return the XML Element for this object """
    
    x = super().__element__(scope=self, tag=tag)
    
    for e in ('id', 'font', 'name', 'vis', 'isroot', 'border', 'title'):
      if hasattr(self, e):
        super().__subelement__(x, e, text=getattr(self, e))
    
    for e in ('screen', 'dimension', 'position', 'coords'):
      if hasattr(self, e):
        super().__subelement__(x, getattr(self,e).__xml__(e))
    
    super().__xml_nodes__(x)
    super().__xml_comments__(x)
    super().__xml_edges__(x)

    return x
