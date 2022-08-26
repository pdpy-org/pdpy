#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
""" arrange1b definition """

__all__ = [ "arrange1b" ]

verbose = 0

if verbose: print("Initialized", __all__[0], "graph placing algorithm.")

def ids(x):
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

def getChildren(o, canvas, port=0):
  """ Returns a the list of children nodes of an object ``o``
  
  Arguments
  ---------
  - The second argument is the ``canvas``, of :class:`Canvas`
  - If ``port`` is set to ``1``, the list contains (obj,port)
  otherwise, it just contains `(obj)`


  """
  if port:
    r = [(canvas.get(e.sink.id), e.source.port) for e in canvas.edges if e.source.id == o.id]
    if verbose: print(o.getname(), "==> (child,port) ==>",list(map(lambda x:[x[0].id,x[0].getname(),x[1]], r)))
    return r
  else:
    r = [canvas.get(e.sink.id) for e in canvas.edges if e.source.id == o.id]
    if verbose: print("Children:", ids(r))
    return r

def y_increment(self, canvas):
  """ This increments the Y cursor of a canvas

  Arguments
  ---------
  ``self`` : the scope of the :class:`PdPy` class
  ``canvas``: the :class:`Canvas` within ``self`` containing the nodes
  
  Returns
  -------
  None
  """
  canvas.__cursor__.y += (self.__vstep__ * self.__max_h__)

def x_increment(self, canvas, port):
  """ This increments the X cursor of a canvas

  Arguments
  ---------
  ``self`` : the scope of the :class:`PdPy` class
  ``canvas``: the :class:`Canvas` within ``self`` containing the nodes
  
  Returns
  -------
  None
  """
  canvas.__cursor__.x += (self.__hstep__ * self.__max_w__ * port)

def arrange1b(self):
  """ Arrange objects on a 2d surface
  
  Description
  -----------
  This function attempts to arrange objects graphically on the canvas.
  It consists of three steps:
  1. step1: Initialization
  2. step2: :func:`step2`
  3. step3: :func:`step3`

  """
  if verbose: print("========= begin arrange algorithm arrange 1b ==========")

  # inicializar
  canvas = self.__last_canvas__()
  if not hasattr(canvas, 'nodes') or len(canvas.nodes) == 0:
    raise ValueError("Canvas", canvas.getname(), "has no nodes.")
  
  X = list(canvas.nodes) # the nodes to place
  Z = [] # the placed nodes

  # Inicializar los maximos de w y h
  self.__max_w__ = max(map(lambda x:x[0],[o.__get_obj_size__() for o in X]))
  self.__max_h__ = max(map(lambda x:x[1],[o.__get_obj_size__() for o in X]))
  
  def relocator(parent, child):
    """ Relocates the ``child`` object based on the ``parent``
    """
    
    if verbose: print("Relocate", child.id, "with", parent.id, "?")
    if verbose: print(child.position.__pd__(), "and", parent.position.__pd__())
    
    if parent in getChildren(child, canvas) and child in getChildren(parent, canvas):
      if verbose: print("CIRCULAR")
      reubicar(parent, self.__hstep__ * self.__max_w__, 0, y=child)

      
    elif child.position.y != parent.position.y:
      if verbose: print("UNEQUAL_Y")
      if child.position.y > parent.position.y:
        if verbose: print("child is AFTER the parent")
        reubicar(parent, self.__hstep__ * self.__max_w__, 0, x=child)
      else:
        if verbose: print("child is BEFORe the parent")
        reubicar(child, 0, self.__vstep__ * self.__max_h__, y=parent)


    elif child.position.y == parent.position.y:
      if verbose: print("EQUAL_Y")
      reubicar(child, 0, self.__vstep__ * self.__max_w__, y=parent)
    else:
      if verbose: print("Leaving", child.id, "as is.")
      return
    
    if verbose: print("--> Relocated to:",child.position.__pd__(), "and", parent.position.__pd__())
  
  def step3(o, C, X):
    if verbose: print("input step3 X:",list(zip(map(lambda x:x.getname(),X),ids(X))))
    if verbose: print(o.id, "is connected to", ids(C))
    for i, c in enumerate(C):
      if isinstance(c, tuple):
        ci = c[0]
        port = c[1]
      else:
        ci = c
        port = 0
      if verbose: print(ci.id, "NOT IN", ids(Z))
      if verbose: print("Ports", port, "index", i)
      
      if port:
        canvas.__cursor__.y = o.position.y
      else:
        y_increment(self, canvas)
      
      x_increment(self, canvas, port)
      
      ubicar(ci, canvas.__cursor__.x, canvas.__cursor__.y, yinc=1)
      
      o = ci
      takeChildren(o, callback=relocator)
      
  def ubicar(obj, xpos=None, ypos=None, yinc=1):
    
    # incrementar Y antes
    if yinc == -1: y_increment(self, canvas)
    
    x = xpos if xpos is not None else canvas.__cursor__.x
    y = ypos if ypos is not None else canvas.__cursor__.y
    
    # ubicarlo
    if verbose: print("Ubicando", obj.id, "=>", x, y)
    obj.addpos(x, y)
    
    # incrementar Y despues
    if yinc == 1: y_increment(self, canvas)
    
    # añadirlo a la lista Z
    Z.append(obj)

  def takeChildren(obj, callback=None):
    if verbose: print("takeChildren:")
    # the actual list of children -> (child,port)
    children = getChildren(obj, canvas, 1)
    if len(children) == 0:
      # no children, so continue with next in line if no callback
      return step2(X) if callback is None else None
    
    C = [] # the list of children taken from x
    try:
      for (child, port) in children:
        child_index = X.index(child)
        child_from_x = X.pop(child_index)
        C.append((child_from_x, port))
    except ValueError: # from X.index(child) not finding it
      if verbose: print(ids(getChildren(obj, canvas)))
      if verbose: print(child.id, "is not connected to anybody.")
      
      if child not in Z:
        if verbose: print("But,", child.id, "is not placed in", ids(Z))
        ubicar(child, yinc = -1)
      else:
        if callback is None:
          reubicar(child, 0, self.__vstep__ * self.__max_h__)
      
      if callback is not None:
        callback(obj, child)
    
    finally:
      if len(C):
        if verbose: print("==> passing to step3")
        # pasar obj y la lista al paso recursivo
        step3(obj, C, X)
      else:
        if verbose: print("<== going back to step2")
        step2(X)
  
  def reubicar(obj, xoffset, yoffset, x=None, y=None):
    if verbose: print("Reubicando", obj.getname())
    xobj = x if x is not None else obj
    yobj = y if y is not None else obj
    ubicar(obj,
      xobj.position.x + xoffset, 
      yobj.position.y + yoffset, 
      yinc = 0
    )
  
  def step2(X):
    if verbose: print("input X:",list(zip(map(lambda x:x.getname(),X),ids(X))))
    if len(X) == 0:
      if verbose: print("===> No more objects to place.")
      return 
    else:
      # tomar el primer elemento de X
      obj = X.pop(0)
      # ubicarlo
      ubicar(obj)
      # tomar de X todos los elemntos cuyo origen es obj
      takeChildren(obj)
        
  
  # begin algorithm
  step2(X)
  
  if verbose: print("------------- end -----------")
  
  return
