#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Canvas Class Definition """


# from ..util.utils import log
from .base import Base
from .classes import Point, Size

__all__ = [
  "Properties",
  "Canvas"
]

class Properties(Base):
  """ Properties for a Pure Data 'canvas' or 'subpatch'

  Description:
  -----------
  An object to represent pd's subpatch properties. The basic properties come
  from the pure data file representation: `#N canvas 0 22 450 300 12;`

  Attributes:
  -----------
  `screen` (`Point`) x-y pair of the top-left window corner on the screen (0,22)
  `dimension` (`Size`) window width and height dimensions (450, 300)
  `font` (`int`) window font size (12)
  `__pdpy__` (`str`) PdPy className (`self.__class__.__name__`)

  """
  def __init__(self, 
               screen = [ 0, 22 ],
               dimen  = [ 450, 300 ],
               font   =   12 ):
    self.screen = Point(screen[0], screen[1])
    self.dimension = Size(dimen[0], dimen[1])
    self.font = self.num(font)
    self.__pdpy__ = self.__class__.__name__
    self.__pad__ = Size(self.font, self.font)
    self.__margin__ = Size(0, 0)
    self.__cursor_init__ = Point(self.font, self.font)
    self.__cursor__ = Point(self.font, self.font)
    self.__box__ = Size(self.font * 1.25, self.font * 2)


class Canvas(Properties):
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
  
  """
  def __init__(self, name = "(subpatch)", vis = 0, id = None, **kwargs):
    super().__init__(**kwargs)

    self.__pdpy__ = self.__class__.__name__
    self.name = name.replace('.pd','')
    if isinstance(vis, str):
      self.vis = vis.lower() == "true"
    else:
      self.vis = self.pdbool(vis)
    self.gop = False
    self.coords = None
    self.position = None
    self.title = None
    self.border = None
    self.id = id
    self.__obj_idx__ = -1


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
    # log(1,"Edge",edge.toJSON())

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
    
    # log(0,"Get Position", self.__cursor__.toJSON())

    return self.__cursor__.x, self.__cursor__.y

  def grow_margins(self, word_length=0):

    len_word = self.__cursor__.x + word_length * self.font

    if len_word >= self.__margin__.width:
      self.__margin__.width = len_word

    self.__cursor__.y += self.__box__.height


  def get_char_dim(self):
    return int(self.dimension.width / self.font * 1.55)

  def addpos(self, x, y):
    self.position = Point(x, y)