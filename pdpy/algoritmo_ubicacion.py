#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
"""
Algoritmo para poner objetos conectados en la pagina
====================================================

Mantener una lista de ``objetos`` cada uno con su ancho y largo en ``w`` y ``h``
Mantener una ``fila``
Mantener una lista de objectos ubicados en la ``pagina``
Mantener una lista de puntos ``C`` que tengan las coordenadas del objeto ``C_i = (O_i_w,O_i_h)``

Paso 0: inicializar
-------------------

- Inicializar el indice de puntos ``i = 0``
- Inicializar ``C_i`` con el punto ``(0, 2H * i)``
- Inicializar ``W`` y ``H`` con el máximo valor de ``w`` y ``h`` de todos los ``objetos``
- Inicializar la ``fila`` con todos los ``objetos``

Paso 1: Poner el elemento en la página
--------------------------------------

1. Quitar el primer elemento de la ``fila`` en la variable ``o``, ``o = fila_i``
2. Obtener todos los ``objetos`` cuyas conexiones tienen como origen a ``o``
   1. si hay, ponerlos en orden en una ``subfila`` y concatenar a derecha ``fila``
   2. si no hay, continuar
3. Chequear si ``o`` ya está en la ``pagina``:
   1. Si **no** está en la ``pagina``: *ubicarlo en la pagina*
      1. Ubicarlo con las coordenadas de ``C_i``
      2. Incrementar el indice de puntos ``i = i + 1``
      3. Agregar el objeto ``o`` a la ``pagina``
      4. Agregar el siguiente punto ``C_i = (0, 2H * i)`` a la lista de puntos
      5. Continuar con el Paso 1 con la nueva ``fila``
   2. Si está en la página: *mover el objeto previo*
      1. obtener el indice previo a ``o`` en ``C``, ``iprev = C <- o``
      2. cambiar el valor de ``C_iprev`` por ``(2W * iprev, C_iprev_h)``
"""

__all__ = [ 'ubicar' ]

from pdpy.classes.point import Point


def ubicar(objetos, callback = lambda p:print(p) ):
  print(len(objetos))
  # declarar
  objetos = [] # cada uno con su ancho y largo en ``w`` y ``h``
  fila = []
  ubicado = [] # en la pagina
  C = [] # lista de puntos

  # inicializar
  
  i = 0 # Inicializar el indice de puntos
  H = 0
  W = 0
  
  # Inicializar ``W`` y ``H`` con el máximo valor de ``w`` y ``h`` de todos los ``objetos``
  for obj in objetos:
    width, height = obj.__get_obj_size__()
    if width >= W:
      W = width
    if height >= H:
      H = height

  # Inicializar ``C_i`` con el punto ``(0, 2H * i)``
  C.append((0, 2*H*i)) 

  # Inicializar la ``fila`` con todos los ``objetos``
  fila = [o for o in objetos]


  def paso1(fila):
    if len(fila) <= 0:
      return 
    
    #1. Quitar el primer elemento de la ``fila`` en la variable ``o``, ``o = fila_i``
    o = fila.pop(0)
    #2. Obtener todos los ``objetos`` cuyas conexiones tienen como origen a ``o``
    subfila = [ obj for obj in objetos if obj.edges.source == o.id ]
    #   1. si hay, ponerlos en orden en una ``subfila`` y concatenar a derecha ``fila``
    if len(subfila) >= 1:
      fila = subfila + fila
    #   2. si no hay, continuar

    #3. Chequear si ``o`` ya está en la ``ubicado``:
    if o not in ubicado:
    #   1. Si **no** está en la ``ubicado``: *ubicarlo en la ubicado*
    #      1. Ubicarlo con las coordenadas de ``C_i``
      callback(C[i])
    #      2. Incrementar el indice de puntos ``i = i + 1``
      i += 1
    #      3. Agregar el objeto ``o`` a la ``ubicado``
      ubicado.append(o)
    #      4. Agregar el siguiente punto ``C_i = (0, 2H * i)`` a la lista de puntos
      C.append((0, 2 * H * i))
    #      5. Continuar con el Paso 1 con la nueva ``fila``

    #   2. Si está en la página: *mover el objeto previo*
    else:
    #      1. obtener el indice previo a ``o`` en ``C``, ``iprev = C <- o``
      for iprev, c in enumerate(C):
        if (o.position.x, o.position.y) == c:
          break
    #      2. cambiar el valor de ``C_iprev`` por ``(2W * iprev, C_iprev_h)``
      C[iprev] = (2 * W * iprev, C[iprev][1])
      objetos.get(iprev).position = Point(C[iprev])
    
    # recurse
    return paso1(fila)

  # iniciar algoritmo
  paso1(fila)
