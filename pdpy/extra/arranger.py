#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
"""
Arranger
========
"""

from ..primitives.point import Point

__all__ = [ "Arranger" ]

class Arranger:
  r""" Arranger objects on a 2d surface
  
  This class attempts to arrange objects graphically on the self.canvas.
  To use, simply import and call the class.

  The main algorithm consists of initialization and three steps:
  
  1. Initialization
  2. step1: :func:`step1`
  3. step2: :func:`step2`
  4. step3: :func:`step3`
  
  Parameters
  ----------

  canvas : :class:`pdpy.Canvas`
    The canvas to arrange
  
  verbose : `bool`
    (optional) set verbosity level (default: `False`)
  
  hstep : `float`
    (optional) set the horizontal step factor for x-increments (default: `1.5`)
    
    This factor multiplies the width maxima of all nodes in a canvas.
  
  vstep : `float`
    (optional) set the vertical step factor for y-increments (default: `1`)
    
    This factor multiplies the height maxima of all nodes in a canvas.

  xmargin : `int`
    (optional) set the initial x margin on the canvas (default: `10`)

  xmargin : `int`
    (optional) set the initial x margin on the canvas (default: `10`)

  Returns
  -------
  
  `None`

  Raises
  ------

  Exception
    if there were errors during arrangement
  
  ValueError
    if the `Canvas` has no nodes to arrange

  Example
  -------

  Import the PdPy and Arranger classes

  >>> from .classes.pdpy import PdPy
  >>> from .util.arrange import Arranger as arranger
  
  Create the PdPy instance (and add some objects)
  
  >>> pd = PdPy()
  
  Call the function

  >>> arranger(p)


  """
  def __init__(self, canvas,
              verbose=False,
              hstep=1.5, vstep=1,
              xmargin=10, ymargin=10):
  
    # inicializar
    self.verbose = verbose
    self.canvas = canvas
    
    self.nodes = True
    self.comments = True

    if not hasattr(self.canvas, 'nodes') or len(self.canvas.nodes) == 0:
      self.__print__("Canvas has no nodes.")
      self.nodes = False

    if not hasattr(self.canvas, 'comments') or len(self.canvas.comments) == 0:
      self.__print__("Canvas has no comments.")
      self.comments = False
    
    
    # the nodes to place
    if self.nodes and self.comments:
      self.O = list(self.canvas.nodes) + list(self.canvas.comments)
    elif self.nodes:
      self.O = list(self.canvas.nodes)
    elif self.comments:
      self.O = list(self.canvas.comments)
    else:
      self.__print__("Nothing to arrange.")
      return
    
    # the horizontal step size for increments
    self.hstep = hstep
    # the vertical step size for increments
    self.vstep = vstep
    # the cursor
    self.margin = Point(x=xmargin, y=ymargin)
    self.cursor = Point(x=self.margin.x, y=self.margin.y)

    self.Z = [] # the placed nodes

    # Inicializar los maximos de w y h
    # self.W = max(map(
    #   lambda x:x[0],
    #   [o.__get_obj_size__(self.canvas) for o in self.O]
    # ))
    # self.H = max(map(
    #   lambda x:x[1],
    #   [o.__get_obj_size__(self.canvas) for o in self.O]
    # ))

    # selfs.y_inc = self.vstep * self.H
    # self.x_inc = self.hstep * self.W

    self.__print__("Initialized", __all__[0], "graph placing algorithm.")
    self.__call__()

  def __call__(self):
    self.__print__("========= begin arrange algorithm ==========")
    
    try:
      self.step1()
    except RecursionError as e:
      raise Exception("There were errors with the arrangement:", e)    
    
    self.__print__("------------- end -----------")

  def __print__(self, *args):
    if self.verbose: print(*args)

  def __ids__(self, x):
    """ Returns the IDs of a list of objects or tuplets of (obj,port)
    This is useful for printing.
    """
    result = []
    for e in x:
      if isinstance(e, tuple):
        result.append((e[0].getid(), e[1]))
      else:
        result.append(e.getid())
    return result

  def __get_children__(self, o, port=0):
    """ Returns a the list of children nodes of an object ``o``
    
    Arguments
    ---------
    - The second argument is the ``canvas``, of :class:`Canvas`
    - If ``port`` is set to ``1``, the list contains (obj,port)
    otherwise, it just contains `(obj)`


    """
    if port:
      r = [(self.canvas.get(e.sink.getid()), e.source.port) for e in self.canvas.edges if e.source.getid() == o.getid()]
      self.__print__(
        "__get_children__():",
        o.getname(), 
        "==>", 
        list(map(lambda x:[x[0].getid(),x[0].getname(),x[1]], r))
      )
      return r
    else:
      r = [self.canvas.get(e.sink.getid()) for e in self.canvas.edges if e.source.getid() == o.getid()]
      self.__print__("__get_children__():", self.__ids__(r))
      return r

  def __y_inc__(self, y_inc):
    """ This increments the Y cursor of a canvas

    Arguments
    ---------
    ``self`` : the canvas of the :class:`PdPy` class
    ``canvas``: the :class:`Canvas` within ``self`` containing the nodes
    
    Returns
    -------
    None
    """
    self.cursor.increment(0, y_inc * self.vstep)

  def __x_inc__(self, x_inc, port = 0):
    """ This increments the self.O cursor of a canvas

    Arguments
    ---------
    ``port`` : the port number to offset (default = 0)
    
    Returns
    -------
    None
    """
    self.cursor.increment(x_inc * port * self.hstep, 0)

  def __place__(self, o, xpos=None, ypos=None, yinc=1):
    """ Place the object on the canvas

    Parameters
    ----------
    o: pdpy object
      the object
    
    xpos: :class:`int`
      The position in the x-axis to place the object
    
    ypos: :class:`int`
      The position in the y-axis to place the object
    
    yinc: :class:`int`
      A flag for y-increments to be performed before ``-1``, after ``1``, or not at all ``0``
    
    
    """
    
    # incrementar Y antes
    if yinc == -1: self.__y_inc__(self.prev_y_inc)
    
    # obtener el tamaño del objeto
    x_inc, y_inc = o.__get_obj_size__(self.canvas)
    
    x_inc += self.margin.x
    y_inc += self.margin.y

    x = xpos if xpos is not None else self.cursor.x
    y = ypos if ypos is not None else self.cursor.y
    
    # placelo
    self.__print__("place():", o.getid(), "=>", x, y)
    o.addpos(x, y)
    # incrementar Y despues
    if yinc == 1: self.__y_inc__(y_inc)
    # añadirlo a la lista Z
    self.Z.append(o)
    # actualizar el tamaño previo
    self.prev_y_inc, self.prev_x_inc = y_inc, x_inc

  def __move__(self, o, xoffset, yoffset, x=None, y=None):
    self.__print__("__move__():", o.getname())
    xobj = x if x is not None else o
    yobj = y if y is not None else o
    
    self.__place__(o,
      xobj.position.x + xoffset, 
      yobj.position.y + yoffset, 
      yinc = 0
    )

  def __relocator__(self, parent, child):
    """ Relocates the ``child`` object based on the ``parent``
    """
    self.__print__("__relocator__()", parent.getid(), child.getid())
    self.__print__(parent.position.__pd__(), "and", child.position.__pd__())
    
    if parent in self.__get_children__(child) and child in self.__get_children__(parent):
      self.__print__("CIRCULAR")
      self.__move__(parent, self.prev_x_inc, 0, y = child)

      
    elif child.position.y != parent.position.y:
      self.__print__("UNEQUAL_Y")
      if child.position.y > parent.position.y:
        self.__print__("child is BELOW the parent")
        xoff = -abs(child.position.x-parent.position.x)
        self.__move__(child, xoff, 0, x = parent)
      else:
        self.__print__("child is ABOVE the parent")
        yoff = -abs(child.position.y-parent.position.y)
        self.__move__(child, 0, yoff, y = parent)

    elif child.position.y == parent.position.y:
      self.__print__("EQUAL_Y")
      self.__move__(child, 0, self.prev_y_inc, y = parent)

    else:
      self.__print__("Leaving", child.getid(), "as is.")
      return
    
    self.__print__("--> Relocated to:",child.position.__pd__(), "and", parent.position.__pd__())
    return
  
  def step3(self, obj, children):
    """ Step3: Place every child

    For every child in the ``children`` list:

    #. Adjust y-position
    #. Adjust x-position
    #. Place the child
    #. Pass the child to :func:`step2` with ``relocate=True``

    Parameters
    ----------

    obj: :class:`pdpy.Object`
      The PdPy object with ``position`` attribute
    
    children: ``list``
      The list of children whose parent is the passed ``obj``

    """
    parent = obj
    self.__print__("="*10,"STEP 3","="*10)
    self.__print__("input", parent.getid(), parent.getname())
    self.__print__(parent.getid(), "is connected to", self.__ids__(children))
    self.__print__(">>>>>>>>>> BEGIN CHILD LOOP for", obj.getname())
    for i, (child, portnum) in enumerate(children):
      self.__print__(">"*4,"Child #"+str(i), child.getid(), child.getname(), portnum)
      self.__print__(">"*4,child.getid(), "NOT IN", self.__ids__(self.Z))
      
      x_inc, y_inc = child.__get_obj_size__(parent.__parent__())

      if portnum:
        self.cursor.y = parent.position.y
      else:
        self.__y_inc__(y_inc)
      
      self.__x_inc__(x_inc, portnum)
      self.__print__("PLACEMENT")
      self.__place__(child,
        self.cursor.x, 
        self.cursor.y, 
        yinc = 0
      )
      self.prev_x_inc = x_inc
      self.prev_y_inc = y_inc
      
      self.step2(child, relocate = True)
    
    self.__print__("<<<<<<<<<< end child loop for", obj.getname())
    self.__print__("-"*10,"(end STEP 3)","-"*10)

  def step2(self, obj, relocate = False):
    """ Step 2: Take the object's children from the object list

    This step takes performs the following instructions:

    #. ``return`` if the `obj` has no children
    #. otherwise, pop all children from the object list
    
    For each child, if the child is not on the object list:
    
    #. If the child is not placed, place it, otherwise move it
    #. If ``relocate`` is ``True``, run the relocator on that child
    
    If there are popped children, pass them to :func:`step3`, otherwise
    
    #. reset y-position
    #. and go back to :func:`step1`

    Parameters
    ----------

    obj: :class:`pdpy.Object`
      A patchable PdPy object based on `object` with a `position` attribute
    
    relocate: ``callback`` or ``None``
      A callback function to perform object relocation

    Returns
    -------

    `None`
    
    """
    
    self.__print__("'"*10,"BEGIN STEP 2","'"*10)
    self.__print__("input", obj.getid(), obj.getname(), relocate.__class__.__name__)

    if not hasattr(self.canvas, 'edges'):
      self.__print__(self.canvas.getname(), "has no connections.")
      return
    # the actual list of children -> (child,port)
    children = self.__get_children__(obj, port = True)

    # no children, so continue with next in line if no relocate
    if not len(children): return
    
    C = [] # the list of children taken from x

    for (child, port) in children:
            
      if child not in self.O:
        self.__print__(child.getid(), "is not connected to anybody.")
        
        if child not in self.Z:
          self.__print__("But,", child.getid(), "is not placed in", self.__ids__(self.Z))
          self.__place__(child, yinc = 1)
        elif relocate is None:
          # move the child if there is no relocate callback
          self.__move__(child, 0, self.y_inc)
        
        # also: run the relocator callback if it is there
        if relocate:
          self.__relocator__(obj, child)
      
        self.__print__(" *** done relocating, continuing")
      
      else:
        self.__print__("child exists, appending", child.getid())
        child_index = self.O.index(child)
        child_from_x = self.O.pop(child_index)
        C.append((child_from_x, port))
      
      if not len(self.O): break

    
    self.__print__("done with child loop", len(C))
    self.__print__("`"*10,"(end STEP 2) for ", obj.getname(),"`"*10)
    if len(C):
      self.__print__("==> passing to step3")
      # pasar obj y la lista al paso recursivo
      self.step3(obj, C)
    else:
      x_inc, _ = obj.__get_obj_size__(self.canvas)
      self.__print__("<== going back to step1")
      self.__x_inc__(x_inc, 1)
      self.prev_x_inc = x_inc
      self.prev_y_inc = 0
      self.cursor.y = self.margin.y
      self.step1()

  def step1(self):
    """ Step 1: Take the object from the object list

    This step takes no arguments and performs the following instructions:

    1. take an object from the object list
    2. place the object
    3. pass the object to :func:`step2` without callback 

    If there are no objects on the list, it returns

    Returns
    -------

    `None`

    """
    self.__print__("~"*10,"STEP 1","~"*10)
    self.__print__("input",list(zip(map(lambda x:x.getname(),self.O),self.__ids__(self.O))))
    
    if len(self.O) == 0:
      self.__print__("#2 ===> No more objects to place.")
      return 
    else:
      # tomar el primer elemento de self.O
      obj = self.O.pop(0)
      # ubicarlo
      self.__place__(obj)
      # tomar de self.O todos los elemntos cuyo origen es obj
      self.step2(obj)
    
    self.__print__("-"*10,"(end STEP 1)","-"*10)
    self.step1()
