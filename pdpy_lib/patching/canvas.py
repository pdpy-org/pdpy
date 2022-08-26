#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
"""
Canvas
======
"""
from ..core.base import Base
from ..core.canvasbase import CanvasBase
from ..primitives.point import Point
from ..primitives.size import Size

__all__ = [ 'Canvas' ]

class Canvas(CanvasBase, Base):
  """ Represents a Pure Data canvas, aka subpatch

  Besides basic properties, the Canvas class takes 
  `#X connect`, `#X coords`, and `#X restore` into its own namespace, 
  as well as the pure data nodes that are created within the context 
  of a subpatch/canvas window. 

  Parameters
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
  def __init__(self, json=None, name=None, **kwargs):

    CanvasBase.__init__(self, obj_idx=-1)
    Base.__init__(self, pdtype='N', cls='canvas')
    self.__pdpy__ = self.__class__.__name__
    
    if json is not None:
      super().__populate__(self, json)
    else:
      default = self.__d__
      self.name = default.name if name is None else self.__sane_name__(name)
      self.root = False
      
      super().__set_default__(kwargs, [
        ('screen', default, lambda d: Point(x=d['x'], y=d['y'])),
        ('dimension', default, lambda d: Size(w=d['width'], h=d['height'])),
        ('font', default, lambda d: d['size']),
        ('vis', default)
      ])
    
      self.isgraph = kwargs.pop('isgraph') if 'isgraph' in kwargs else False

    if hasattr(self, 'isroot'):
      self.isroot = self.__pdbool__(self.isroot)
      
    
    if hasattr(self, 'font'):
      self.font = self.__num__(self.font)
      self.__pad__ = Size(w=self.font, h=self.font)
      self.__cursor_init__ = Point(x=self.font, y=self.font)
      self.__cursor__ = Point(x=self.font, y=self.font)
      self.__box__ = Size(w=int(self.font * 1.25), h=int(self.font * 2))
      self.__margin__ = Size(w=self.font, h=self.font)

  def update_cursor(self, w_step=0, h_step=0):
    """ Fill objects from top to bottom until we reach bottom
    (used to be get_position)
    """
    print("Update Cursor:", w_step, h_step)
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
    self.__cursor__.x += w_step

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
