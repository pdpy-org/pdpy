#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Canvas Base Class Definition """

from .xmlbuilder import XmlBuilder

__all__ = [ 'CanvasBase' ]

class CanvasBase(XmlBuilder):
  """ Base class for a canvas -- used by pdpy.pdpy and pdpy.canvas """

  def __init__(self, obj_idx=0, isroot=False):
    """ Initialize the canvas base class """
    super().__init__()
    
    if isroot:
      self.isroot = isroot
    
    self.__obj_idx__ = obj_idx
    
    # This is a dictionary with 
    # - the node indices as keys, and 
    # - the last self.__depth_list__ index as values
    self.__obj_map__ = {}
    
  def __update_obj_map__(self, x):
    """ Update the object map with the current object

    Description:
    ------------
    This method updates the object map with the current object. This is meant
    to keep track of the objects in the current canvas, so we can connect
    them later with their respective edges.
    """
    # If the node has an ID, get it and use it to update the object map
    if hasattr(x, "id"):
      # increment the index by one
      self.__obj_idx__ += 1
      # add the node to the map so that 
      # key is the id and value is the index
      self.__obj_map__.update({
        int(getattr(x,'id')) : self.__obj_idx__
      })
  
  def __edges__(self, s):
    for x in getattr(self, 'edges', []):
      s += x.__pd__(self.__obj_map__)
    return s

  def __nodes__(self, s):
    for x in getattr(self, 'nodes', []):
      self.__update_obj_map__(x)
      s += x.__pd__()
    return s

  def __comments__(self, s):
    for x in getattr(self, 'comments', []):
      s += x.__pd__()
    return s

  def __coords__(self, s):
    if hasattr(self, 'coords'):
      s += self.coords.__pd__()
    return s

  def __restore__(self, s, isgraph=False):
    if hasattr(self, 'position'):
      s += "#X restore " + self.position.__pd__()
      if hasattr(self, 'title'):
        s += " " + self.title
      if isgraph:
        s += " graph"
      s += self.__end__
    return s
  
  def __render__(self, s, isroot=False, isgraph=False):
    s = self.__nodes__(s)
    s = self.__comments__(s)
    if isroot:
      # argh, this order is swapped for the root canvas
      s = self.__coords__(s)
      s = self.__edges__(s)
    else:
      s = self.__edges__(s)
      s = self.__coords__(s)
    s = self.__restore__(s, isgraph=isgraph)
    return s
  
  def __xml_nodes__(self, parent):
    if hasattr(self, 'nodes'):
      nodes = super().__element__(tag='nodes')
      for e in getattr(self, 'nodes', []):
        self.__update_obj_map__(e)
        super().__subelement__(nodes, e.__xml__())
      super().__subelement__(parent, nodes)

  def __xml_comments__(self, parent):
    if hasattr(self, 'comments'):
      comments = super().__element__(tag='comments')
      for e in getattr(self, 'comments', []):
        super().__subelement__(comments, e.__xml__())
      super().__subelement__(parent, comments)

  def __xml_edges__(self, parent):
    if hasattr(self, 'edges'):
      edges = super().__element__(tag='edges')
      for e in getattr(self, 'edges', []):
        super().__subelement__(edges, e.__xml__(self.__obj_map__))
      super().__subelement__(parent, edges)
