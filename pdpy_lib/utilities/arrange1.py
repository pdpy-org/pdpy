#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
""" arrange1 definition """

__all__ = [ "arrange1" ]

def arrange1(self):

    # inicializar
    canvas = self.__last_canvas__()
    canvas.__cursor__.x = 10
    canvas.__cursor__.y = 10
    self.__hstep__ = 1.25
    self.__vstep__ = 1
    Z = [] # the placed nodes
    C = [] # the list of connections

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
        result = [(canvas.get(e.sink.id), e.source.port) for e in canvas.edges if e.source.id == o.id]
        print("Children:",result)
        return result
      else:
        return [canvas.get(e.sink.id) for e in canvas.edges if e.source.id == o.id]

    def step3(o, C):
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
        
        if port >= 1:
          canvas.__cursor__.y = o.position.y
        else:
          canvas.__cursor__.y += (self.__vstep__ * self.__max_h__)
        canvas.__cursor__.x += (self.__hstep__ * self.__max_w__ * port)
        
        ci.addpos(canvas.__cursor__.x, canvas.__cursor__.y)
        
        o = ci
        Z.append(ci)
        C = []
        try:
          for (child, port) in _children(o, 1):
            C.append((X.pop(X.index(child)), port))
        except ValueError:
          
          print(">> Object >>", child.id, "named", child.getname(), "not in X list")
          
          if child not in Z:
            print("But,", child.id, "is not placed in", ids(Z))
            raise Exception("What sourcery is this?")
          
          print("Relocate", child.id, "with", ci.id, "?")
          print(child.position.__pd__(), "and", ci.position.__pd__())
          
          if ci in _children(child) and child in _children(ci):
            print("CIRCULAR")
            ci.addpos(ci.position.x + self.__hstep__ * self.__max_w__, child.position.y + self.__vstep__ * self.__max_h__)
          elif child.position.y != ci.position.y:
            print("UNEQUAL_Y")
            ci.addpos(ci.position.x + ci.position.x + self.__hstep__ * self.__max_w__, child.position.y)
          elif child.position.y == ci.position.y:
            print("EQUAL_Y")
            child.addpos(child.position.x, child.position.y + self.__hstep__ * self.__max_w__)
          else:
            print("Leaving", child.id, "as is.")
          
          print("--> Relocated to:",child.position.__pd__(), "and", ci.position.__pd__())
        
        finally:
          # canvas.__cursor__.y -= (len(_children(o)))
          step3(o, C)

    X = list(canvas.nodes) # the nodes to place
    # tomar el primer elemento de X
    obj = X.pop(0)
    # ubicarlo
    obj.addpos(canvas.__cursor__.x, canvas.__cursor__.y)
    # incrementar Y
    canvas.__cursor__.y += (self.__vstep__ * self.__max_h__)
    # añadirlo a la lista Z
    Z.append(obj)
    # tomar de X todos los elemntos cuyo origen es obj
    C = list(map(lambda x: X.pop(X.index(x[0])), _children(obj, 1)))
    
    # pasar obj y la lista al paso recursivo
    step3(obj, C)
    
    return