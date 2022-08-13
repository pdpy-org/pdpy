#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
""" arrange1b definition """

from ..classes.point import Point

__all__ = [ "Arrange" ]

class Arrange:
  
  def __init__(self, scope):
    """ Arrange objects on a 2d surface
    
    Description
    -----------
    This class attempts to arrange objects graphically on the self.canvas.
    It consists of three steps:
    
    1. step1: Initialization
    2. step1: :func:`step1`
    3. step3: :func:`step3`

    """
    # inicializar
    self.canvas = scope.__last_canvas__()
    
    if not hasattr(self.canvas, 'nodes') or len(self.canvas.nodes) == 0:
      raise ValueError("Canvas", self.canvas.getname(), "has no nodes.")

    self.verbose = True
    # the horizontal step size for increments
    self.hstep = 1.5 
    # the vertical step size for increments
    self.vstep = 1
    # the cursor
    self.cursor = Point(x=10, y=10)
    
    self.O = list(self.canvas.nodes) # the nodes to place
    self.Z = [] # the placed nodes

    # Inicializar los maximos de w y h
    self.W = max(map(lambda x:x[0],[o.__get_obj_size__() for o in self.O]))
    self.H = max(map(lambda x:x[1],[o.__get_obj_size__() for o in self.O]))

    self.y_inc = self.vstep * self.H
    self.x_inc = self.hstep * self.W

    print("Initialized", __all__[0], "graph placing algorithm.")
    self.__call__()


  def ids(self, x):
    """ Returns the IDs of a list of objects or tuplets of (obj,port)
    This is useful for printing.
    """
    result = []
    for e in x:
      if isinstance(e, tuple):
        result.append((e[0].id, e[1]))
      else:
        result.append(e.id)
    return result

  def getChildren(self, o, port=0):
    """ Returns a the list of children nodes of an object ``o``
    
    Arguments
    ---------
    - The second argument is the ``canvas``, of :class:`Canvas`
    - If ``port`` is set to ``1``, the list contains (obj,port)
    otherwise, it just contains `(obj)`


    """
    if port:
      r = [(self.canvas.get(e.sink.id), e.source.port) for e in self.canvas.edges if e.source.id == o.id]
      self.print(
        "getChildren():",
        o.getname(), 
        "==>", 
        list(map(lambda x:[x[0].id,x[0].getname(),x[1]], r))
      )
      return r
    else:
      r = [self.canvas.get(e.sink.id) for e in self.canvas.edges if e.source.id == o.id]
      self.print("getChildren():", self.ids(r))
      return r

  def y_increment(self):
    """ This increments the Y cursor of a canvas

    Arguments
    ---------
    ``self`` : the scope of the :class:`PdPy` class
    ``canvas``: the :class:`Canvas` within ``self`` containing the nodes
    
    Returns
    -------
    None
    """
    self.cursor.increment(0, self.y_inc)

  def x_increment(self, port):
    """ This increments the self.O cursor of a canvas

    Arguments
    ---------
    ``self`` : the scope of the :class:`PdPy` class
    ``canvas``: the :class:`Canvas` within ``self`` containing the nodes
    
    Returns
    -------
    None
    """
    self.cursor.increment(self.x_inc * port, 0)

  def place(self, o, xpos=None, ypos=None, yinc=1):
    """ Place the object on the canvas

    Arguments
    ---------
    ``o``: the object
    ``xpos``: the position 
    """
      
    # incrementar Y antes
    if yinc == -1: self.y_increment()
    
    x = xpos if xpos is not None else self.cursor.x
    y = ypos if ypos is not None else self.cursor.y
    
    # placelo
    self.print("place():", o.id, "=>", x, y)
    o.addpos(x, y)
    
    # incrementar Y despues
    if yinc == 1: self.y_increment()
    
    # añadirlo a la lista Z
    self.Z.append(o)

  def move(self, o, xoffset, yoffset, x=None, y=None):
    self.print("move():", o.getname())
    xobj = x if x is not None else o
    yobj = y if y is not None else o
    
    self.place(o,
      xobj.position.x + xoffset, 
      yobj.position.y + yoffset, 
      yinc = 0
    )

  def relocator(self, parent, child):
    """ Relocates the ``child`` object based on the ``parent``
    """
    self.print("relocator()", parent.id, child.id)
    self.print(parent.position.__pd__(), "and", child.position.__pd__())
    
    if parent in self.getChildren(child) and child in self.getChildren(parent):
      self.print("CIRCULAR")
      self.move(parent, self.x_inc, 0, y = child)

      
    elif child.position.y != parent.position.y:
      self.print("UNEQUAL_Y")
      if child.position.y > parent.position.y:
        self.print("child is BELOW the parent")
        xoff = -abs(child.position.x-parent.position.x)
        self.move(child, xoff, 0, x = parent)
      else:
        self.print("child is ABOVE the parent")
        yoff = -abs(child.position.y-parent.position.y)
        self.move(child, 0, yoff, y = parent)

    elif child.position.y == parent.position.y:
      self.print("EQUAL_Y")
      self.move(child, 0, self.y_inc, y = parent)

    else:
      self.print("Leaving", child.id, "as is.")
      return
    
    self.print("--> Relocated to:",child.position.__pd__(), "and", parent.position.__pd__())
    return
  
  def step3(self, o, children):
    parent = o
    self.print("="*10,"STEP 3","="*10)
    self.print("input", parent.id, parent.getname())
    self.print(parent.id, "is connected to", self.ids(children))
    self.print(">>>>>>>>>> BEGIN CHILD LOOP for", o.getname())
    for i, (child, portnum) in enumerate(children):
      self.print(">"*4,"Child #"+str(i), child.id, child.getname(), portnum)
      self.print(">"*4,child.id, "NOT IN", self.ids(self.Z))
      
      if portnum:
        self.cursor.y = parent.position.y
      else:
        self.y_increment()
      
      self.x_increment(portnum)
      self.print("PLACEMENT")
      self.place(child,
        self.cursor.x, 
        self.cursor.y, 
        yinc = 0
      )
      self.step2(child, relocate = self.relocator)
      # if self.step2(child, relocate = self.relocator): continue
    
    self.print("<<<<<<<<<< end child loop for", o.getname())
    self.print("-"*10,"(end STEP 3)","-"*10)

  def step2(self, obj, relocate=None):
    
    self.print("'"*10,"BEGIN STEP 2","'"*10)
    self.print("input", obj.id, obj.getname(), relocate.__class__.__name__)


    # the actual list of children -> (child,port)
    children = self.getChildren(obj, port = True)

    # no children, so continue with next in line if no relocate
    if not len(children): return
    
    C = [] # the list of children taken from x

    for (child, port) in children:
            
      if child not in self.O:
        self.print(child.id, "is not connected to anybody.")
        
        if child not in self.Z:
          self.print("But,", child.id, "is not placed in", self.ids(self.Z))
          self.place(child, yinc = -1)
        elif relocate is None:
          # move the child if there is no relocate callback
          self.move(child, 0, self.y_inc)
        
        # also: run the relocate callback if it is there
        if relocate is not None:
          relocate(obj, child)
      
        self.print(" *** done relocating, continuing")
      
      else:
        self.print("child exists, appending", child.id)
        child_index = self.O.index(child)
        child_from_x = self.O.pop(child_index)
        C.append((child_from_x, port))
      
      if not len(self.O): break

    
    self.print("done with child loop", len(C))
    self.print("`"*10,"(end STEP 2) for ", obj.getname(),"`"*10)
    if len(C):
      self.print("==> passing to step3")
      # pasar obj y la lista al paso recursivo
      self.step3(obj, C)
    else:
      self.print("<== going back to step1")
      self.step1()


  def step1(self):
    self.print("~"*10,"STEP 1","~"*10)
    self.print("input",list(zip(map(lambda x:x.getname(),self.O),self.ids(self.O))))
    
    if len(self.O) == 0:
      self.print("#2 ===> No more objects to place.")
      return 
    else:
      # tomar el primer elemento de self.O
      obj = self.O.pop(0)
      # ubicarlo
      self.place(obj)
      # tomar de self.O todos los elemntos cuyo origen es obj
      self.step2(obj)
    
    self.print("-"*10,"(end STEP 1)","-"*10)
    self.step1()
  
  def print(self, *args):
    if self.verbose: print(*args)

  def __call__(self):
    self.print("========= begin arrange algorithm arrange 1b ==========")
    # begin algorithm
    if self.step1():
      raise Exception("There were errors with the arrangement.")    
    self.print("------------- end -----------")
    
    return
