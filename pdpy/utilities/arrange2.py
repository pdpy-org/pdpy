#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
""" arrange2 definition """

__all__ = [ "arrange2" ]

def arrange2(self):
    canvas = self.__last_canvas__()
    self.__u__ = []
    canvas.__cursor__.x = 0
    canvas.__cursor__.y = 0
    self.__level__ = 0
    def _print(level, *message): print(self.__level__*"\t", level*"\t", *message)

    # paso 1:
    def paso1(objetos):
      self.__level__ += 1
      _print(1, "Paso 1:")
      # elegir el primer objeto que no está en la página
      no_obj = True
      for o in objetos:
        if o not in self.__u__:
          no_obj = False
          break
      if no_obj:
        _print(1, "No objects found")
        return
      else:
        # goto 2
        return paso2(o)
    
    def paso2(obj, parent=None, idx=None):
      self.__level__ += 1
      _print(2, "Paso 2")
      # paso 2:
      # ¿esta el objeto en la pagina?
      if obj in self.__u__:
        _print(2, "obj is ubicado")
        # si, 
        # reubicar el objeto que llamó esta conexión
        # al lado de este objeto si y solo si 
        # no estan ya en la misma fila (canvas.__cursor__.x)
        # return
        par_pos = (parent.position.x, parent.position.y)
        obj_pos = (obj.position.x, obj.position.y)
        _print(2, "parent and child position:", par_pos, obj_pos)
        if par_pos[0] != obj_pos[0]:
          _print(2, "diff parent and obj position")
          canvas.__cursor__.x += (1 + idx)
          canvas.__cursor__.y += 1
          parent.addpos(canvas.__cursor__.x, canvas.__cursor__.y)
        else:
          _print(2, "SAME pos", obj.id, parent.id)
        return
      else:
        _print(2, "Not ubicado, placing", obj.id)
        # if parent is not None and idx is not None:
          # canvas.__cursor__.x += (1 + idx)
        obj.addpos(canvas.__cursor__.x, canvas.__cursor__.y)
        canvas.__cursor__.y += 1
        # goto 3

      # paso 3:
        self.__level__ += 1
        _print(3,"Paso 3")
        # ¿tiene conexiones?
        # Returns a list of connected objets ordered by obj's ports or None
        _print(3,"-- Get Connections --")
        conexiones = []
        children = [edge for edge in canvas.edges if obj.id == edge.source.id]
        
        if len(children):
          children_sorted = reversed(sorted(children, key=lambda e:e.source.port))
          conexiones = list(map(lambda e:canvas.get(e.sink.id), children_sorted))

          _print(3,obj.id, "is connected to", list(map(lambda x:x.id, conexiones)))
          for i, conn in enumerate(conexiones):
            # run conn in paso 2:
            _print(3,"CONNECTION:", conn.id)
            self.__level__ -= 1
            paso2(conn, parent=obj, idx=i)
        
        else:
          _print(3,obj.id, "is an endpoint.")
          
          self.__level__ -= 2
          paso1(canvas.nodes)

    # paso 4:
    # ir al paso 1:
    # def paso4():
      # return paso1(canvas.nodes)
    paso1(canvas.nodes)
    
    # paso 5:
    # terminar
    return
