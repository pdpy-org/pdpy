#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
""" arrange definition """

__all__ = [ "arrange", "addxy" ]

def arrange(self):

  canvas = self.__last_canvas__()

  # declarar
  # cada uno con su ancho y largo en ``w`` y ``h``
  objetos = list(canvas.nodes)
  fila = []
  self.__u__ = [] # en la pagina
  C = [] # lista de puntos

  # inicializar
  
  # Inicializar el indice de puntos
  self.__pidx__ = 0
  self.__hstep__ = 1.25
  self.__vstep__ = 1.25
  
  # Inicializar ``W`` y ``H`` con el máximo valor de ``w`` y ``h`` de todos los ``objetos``
  for obj in objetos:
    width, height = obj.__get_obj_size__()
    if width >= self.__max_w__:
      self.__max_w__ = width
    if height >= self.__max_h__:
      self.__max_h__ = height

  # Inicializar ``C_i`` con el punto ``(W,H)``
  C.append((10, 10)) 

  # Inicializar la ``fila`` con todos los ``objetos``
  fila = list(objetos)

  def acomodador(fila):

    if len(fila) <= 0:
      # print("---- end ----")
      return 
    # print("--------------------- begin ---------------------")
    # 1. Quitar el primer elemento de la fila y ponerlo en ``o``
    o = fila.pop(0)
    
    # uncomment for prints
    # namit = lambda objs: list(map(lambda x: x.getname(),objs)) 
    
    # 2. Obtener todos los nodos cuyas conexiones que
    #    tienen como origen a ``o`` y no estan ya self.__u__.
    #    Para esto, iteramos sobre los bordes/conexiones
    subfila = sorted([ canvas.get(edge.sink.id) for edge in canvas.edges if edge.source.id == o.id and o.id not in self.__u__], key=lambda x:x.id)
    
    # print(("Objeto:",o.getname(), o.id))
    # print("Resto:",namit(fila))
    # print("SUBFILA:", namit(subfila))
    # print("self.__u__:", self.__u__)
    
    # 3. Chequear si ``o`` ya está en la ``self.__u__``:
    #   1. Si **no** está en la ``self.__u__``: *ubicarlo en la self.__u__*
    if o.id not in self.__u__:
      # print("Not located yet:", (o.getname(),o.id))
    #   1. Ubicarlo con las coordenadas de ``C_i``
      o.addpos(*C[self.__pidx__])
    #   2. Agregar el objeto ``o`` a la ``self.__u__``
      self.__u__.append(o.id)
    #   3. Agregar el siguiente punto a la lista de puntos
    #    - en x: ponemos el valor de C_i_x en ese punto
      x = C[self.__pidx__][0]
    #    - en y: incrementamos el valor de C_i_y con ``V * H``, donde
    #    V es el factor de estiramiento vertical,
    #    H es el máximo valor de y que existe en ``objetos``
      y = C[self.__pidx__][1] + self.__vstep__ * self.__max_h__
    #   Esto queda en:
      C.append((x, y))
    #   4. Incrementar el indice de puntos ``i = i + 1``
      self.__pidx__ += 1
    #   5. paso recursivo con la nueva ``fila``

    # 2. Si está en la página: *mover el objeto previo*
    else:
      # print("It is already here: ", o.getname())
    #   1. obtener el indice previo a ``o`` en ``C``, ``iprev = C <- o``
      # print(C)
      for iprev, c in enumerate(C):
        if (o.position.x, o.position.y) == c:
          break
      # dijimos el previo
      iprev -= 2
      # proteger en caso del primer objeto
      iprev = 0 if iprev < 0 else iprev
      # print(o.getname(), "found in C at", str(iprev))
    #   2. cambiar el valor de ``C_iprev`` por ``(2W * iprev, C_iprev_h)``
      x = C[iprev][0] + self.__hstep__ * self.__max_w__
      y = C[iprev][1] + self.__vstep__ * self.__max_h__
      C[iprev] = (x, y)
    #   3. actualizar la posición de ese objeto 
      canvas.get(iprev).addpos(*C[iprev])
    
    #1. si hay, ponerlos en orden en una ``subfila`` y concatenar a derecha ``fila``
    if len(subfila) >= 1:
      # print(namit([o]), "Is connected to", namit(subfila))
      acomodador(subfila)
    
    #2. si no hay, continuar
    # recurse
    return acomodador(fila)

  # iniciar algoritmo
  acomodador(fila)
  print("Done arranging")
  for n in canvas.nodes:
    print(n.getname(), n.position.__pd__())




def addxy(self, nodes, canvas):
  """ This function is called by ``PdPy.arrange()``
  """
  
  if nodes is None or canvas is None:
    raise Exception("Must provide a node and a canvas.")

  # make sure nodes are iterable
  if type(nodes) not in (tuple, list):
    nodes = [nodes]
  
  # check the size of all nodes 
  # increment the stored max height and width
  for node in nodes:
    width, height = node.__get_obj_size__()
    if width >= self.__max_w__:
      self.__max_w__ = width
    if height >= self.__max_h__:
      self.__max_h__ = height

  # print("addXY: length ", len(nodes))
  
  if len(nodes) == 0:
    raise Exception("No nodes provided in: ", nodes)
  elif len(nodes) == 1:
    # there is only one node,
    # place the node at the current cursor
    node[0].addpos(canvas.__cursor__.x,canvas.__cursor__.y)
    # update the cursor offsetting it VERTICALLY
    canvas.update_cursor(w_step=0, h_step=self.__max_h__)
  else:    
    # there is a group of nodes to connect
    for node in nodes:
      node.addpos(canvas.__cursor__.x,canvas.__cursor__.y)
      canvas.update_cursor(w_step=self.__max_w__, h_step=self.__max_h__)
