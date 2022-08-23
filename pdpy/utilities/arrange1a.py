#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
""" arrange1a definition """

__all__ = [ "arrange1a" ]

print("Initialized", __all__[0], "graph placing algorithm.")

def arrange1a(self):
  print("========= begin arrange algorithm arrange 1b ==========")

  # inicializar
  canvas = self.__last_canvas__()
  X = list(canvas.nodes) # the nodes to place
  canvas.__cursor__.x = 10
  canvas.__cursor__.y = 10
  self.__hstep__ = 1.25
  self.__vstep__ = 1
  Z = [] # the placed nodes

  # Inicializar los maximos de w y h
  for obj in canvas.nodes:
    width, height = obj.__get_obj_size__()
    if width >= self.__max_w__:
      self.__max_w__ = width
    if height >= self.__max_h__:
      self.__max_h__ = height

  def ids(x):
    result = []
    for e in x:
      if isinstance(e, tuple):
        result.append((e[0].id, e[1]))
      else:
        result.append(e.id)
    return result

  
  def _children(o, port=0):
    if port:
      r = [(canvas.get(e.sink.id), e.source.port) for e in canvas.edges if e.source.id == o.id]
      print("Children-Port:",list(map(lambda x:[x[0].id,x[0].getname(),x[1]], r)))
      return r
    else:
      r = [canvas.get(e.sink.id) for e in canvas.edges if e.source.id == o.id]
      print("Children:", ids(r))
      return r

  def step3(o, C, X):
    print("input step3 X:",list(zip(map(lambda x:x.getname(),X),ids(X))))
    print(o.id, "is connected to", ids(C))
    for i, c in enumerate(C):
      if isinstance(c, tuple):
        ci = c[0]
        port = c[1]
      else:
        ci = c
        port = 0
      print(ci.id, "NOT IN", ids(Z))
      print("Ports", port, "index", i)
      
      if port:
        canvas.__cursor__.y = o.position.y
      else:
        canvas.__cursor__.y += (self.__vstep__ * self.__max_h__)
      canvas.__cursor__.x += (self.__hstep__ * self.__max_w__ * port)
      
      ubicar(ci, canvas.__cursor__.x, canvas.__cursor__.y, yinc=False)
      
      o = ci
      
      SUBC = []
      try:
        for (child, port) in _children(o, 1):
          SUBC.append((X.pop(X.index(child)), port))
      except ValueError:
        
        print(">> Object >>", child.id, "named", child.getname(), "not in X list")
        
        if child not in Z:
          print("But,", child.id, "is not placed in", ids(Z))
          ubicar(child)
        
        print("Relocate", child.id, "with", ci.id, "?")
        print(child.position.__pd__(), "and", ci.position.__pd__())
        
        if ci in _children(child) and child in _children(ci):
          print("CIRCULAR")
          reubicar(ci, self.__hstep__ * self.__max_w__, 0, y=child)
          
        elif child.position.y != ci.position.y:
          print("UNEQUAL_Y")
          reubicar(ci, self.__hstep__ * self.__max_w__, 0)

        elif child.position.y == ci.position.y:
          print("EQUAL_Y")
          reubicar(child, 0, self.__vstep__ * self.__max_w__, y=ci)
        else:
          print("Leaving", child.id, "as is.")
        
        print("--> Relocated to:",child.position.__pd__(), "and", ci.position.__pd__())
      
      finally:
        
        if len(C) == 0:
          print(o.id, "has no children.")
          step1(X)
        else:
          print("==> recursive step ==>")
          step3(o, SUBC, X)

  def ubicar(obj, xpos=None, ypos=None, yinc=True):
    x = xpos if xpos is not None else canvas.__cursor__.x
    y = ypos if ypos is not None else canvas.__cursor__.y
    print("Ubicando", obj, "=>", x, y)
    # ubicarlo
    obj.addpos(x, y)
    # incrementar Y
    if yinc:
      canvas.__cursor__.y += (self.__vstep__ * self.__max_h__)
    # añadirlo a la lista Z
    Z.append(obj)

  def takeChildren(obj):
    children = _children(obj, 1) # the actual list of children -> (child,port)
    C = [] # the list of children taken from x
    try:
      for (child, port) in children:
        child_index = X.index(child)
        child_from_x = X.pop(child_index)
        C.append((child_from_x, port))
    except ValueError:
      print(ids(_children(obj)))
      print(child.id, "is not connected to anybody.")
      if child not in Z:
        ubicar(child)
      else:
        reubicar(child, 0, self.__vstep__ * self.__max_h__)
    finally:
      return C
  
  def reubicar(obj, xoffset, yoffset, x=None, y=None):
    print("Reubicando", obj)
    xobj = x if x is not None else obj
    yobj = y if y is not None else obj
    ubicar(obj,
      xobj.position.x + xoffset, 
      yobj.position.y + yoffset, 
      yinc = False
    )
  
  def step1(X):
    print("input X:",list(zip(map(lambda x:x.getname(),X),ids(X))))
    if len(X) == 0:
      print("===> No more objects to place.")
      return 
    else:
      # tomar el primer elemento de X
      obj = X.pop(0)
      # ubicarlo
      ubicar(obj)
      # tomar de X todos los elemntos cuyo origen es obj
      children = takeChildren(obj)
      if len(children):
        # pasar obj y la lista al paso recursivo
        step3(obj, children, X)
      else:
        step1(X)
  

  step1(X)
  print("------------- end -----------")
  return
