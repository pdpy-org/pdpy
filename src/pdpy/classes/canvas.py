#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Canvas Class Definition """

from .base import Base
from .classes import Point, Size

__all__ = [
  "Canvas"
]
class Canvas(Base):
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
  - `coords`   (`Coords`) Object holding coordinates necessary for GOP (None)  
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

    super().__init__(pdtype='N', cls='canvas')
    self.__pdpy__ = self.__class__.__name__
    self.isroot = False
    self.__obj_idx__ = -1
    # This is a dictionary with 
    # - the node indices as keys, and 
    # - the last self.__depth_list__ index as values
    self.__obj_map__ = {}
    
    if json is not None:
      super().__populate__(self, json)
    else:
      self.screen = Point(x=0, y=22)
      self.dimension = Size(w=450, h=300)
      self.font = 12
      self.vis = 0
      self.name = None
    
    self.isroot = self.__pdbool__(self.isroot)
    
    if hasattr(self, 'font'):
      self.font = self.__num__(self.font)
      self.__pad__ = Size(w=self.font, h=self.font)
      self.__cursor_init__ = Point(x=self.font, y=self.font)
      self.__cursor__ = Point(x=self.font, y=self.font)
      self.__box__ = Size(w=self.font * 1.25, h=self.font * 2)
      self.__margin__ = Size()

  def __update_obj_map__(self, x):
    """ Update the object map with the current object

    Description:
    ------------
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
    self.edges.append(edge)
    # log(1,"Edge",edge.__json__())

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

  def get_position(self):
    """ Fill objects from top to bottom until we reach bottom
    """
    
    # log(1,"Get Position", f"PAD X:{self.__pad__.width}, pad Y:{self.__pad__.height}")
    max_x = self.dimension.width - self.__pad__.width
    max_y = self.dimension.height - self.__pad__.height
    # log(1,"Get Position", f"MAX X:{max_x}, MAX Y:{max_y}")
    if self.__cursor__.y >= max_y:
      # log(1,"Get Position", "Reset Y")
      # reset y and increment x position
      self.__cursor__.y = self.__margin__.height + self.__box__.height
      self.__cursor__.x += self.__margin__.width
    
    if self.__cursor__.x >= max_x:
      # log(1,"Get Position", "Reset X")
      # reset x and increment y position
      self.__cursor__.x = self.__cursor_init__.x
      self.__cursor__.y *= 2
    
    # however, if cursor is out of bounds, grow downwards...
      # reset x, 
      # resize the canvas to be twice as tall as before
      # and make y be the bottom most position
    if self.__cursor__.y >= max_y and self.__cursor__.x >= max_x:
      # log(1,"Get Position", "Out of Bounds")
      self.__cursor__.x = self.__cursor_init__
      self.dimension.height *= 2
      self.__cursor__.y += self.dimension.height 
      self.__cursor__.y += self.__pad__.height 
      self.__cursor__.y += self.__box__.height
    
    # log(0,"Get Position", self.__cursor__.__json__())

    return self.__cursor__.x, self.__cursor__.y

  def grow_margins(self, word_length=0):

    len_word = self.__cursor__.x + word_length * self.font

    if len_word >= self.__margin__.width:
      self.__margin__.width = len_word

    self.__cursor__.y += self.__box__.height


  def get_char_dim(self):
    return int(self.dimension.width / self.font * 1.55)

  def addpos(self, x, y):
    setattr(self, 'position', Point(x=x, y=y))

  def __pd__(self):
    """ Pure Data representation of the canvas """

    # the canvas line
    s = super().__pd__()
    s += f" {self.screen.__pd__()} {self.dimension.__pd__()}"
    
    if self.isroot:
      # root canvas only reports font
      s += f" {self.font}"
    else:
      # non-root canvases, report their name and their vis status
      s += f" {self.name} {1 if self.vis else 0}"
    
    # end the line so we can continue appending to `s`
    s += self.__end__
    
    # recurse through the nodes
    for x in getattr(self,'nodes',[]):
      # print(1,"Canvas", f"Node: {x.__json__()}")
      self.__update_obj_map__(x)
      s += f"{x.__pd__()}"

    # recurse through the comments
    for x in getattr(self,'comments', []):
      s += f"{x.__pd__()}"
    
    # connections and coords
    # this order is swapped for the root canvas
    if self.isroot:
      if hasattr(self, 'coords'):
        s += self.coords.__pd__()
      for x in getattr(self, 'edges', []):
        s += f"{x.__pd__(self.__obj_map__)}"
    else:
      for x in getattr(self, 'edges', []):
        s += f"{x.__pd__(self.__obj_map__)}"
      if hasattr(self, 'coords'):
        s += self.coords.__pd__()
    
    # the restore line
    if hasattr(self, 'position'):
      s += f"#X restore {self.position.__pd__()}"
      if hasattr(self, 'title'):
        s += f" {self.title}"
      s += self.__end__
    
    # the border, only if not root
    if not self.isroot and hasattr(self, 'border'):
      s += f"#X f {self.border} {self.__end__}"

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
    
    if hasattr(self, 'nodes'):
      nodes = super().__element__(tag='nodes')
      for e in getattr(self, 'nodes', []):
        self.__update_obj_map__(e)
        super().__subelement__(nodes, e.__xml__())
      super().__subelement__(x, nodes)

    if hasattr(self, 'comments'):
      comments = super().__element__(tag='comments')
      for e in getattr(self, 'comments', []):
        super().__subelement__(comments, e.__xml__())
      super().__subelement__(x, comments)

    if hasattr(self, 'edges'):
      edges = super().__element__(tag='edges')
      for e in getattr(self, 'edges', []):
        super().__subelement__(edges, e.__xml__(self.__obj_map__))
      super().__subelement__(x, edges)
          
    return x
