#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Canvas Base Class Definition """

__all__ = [ 'CanvasBase' ]

class CanvasBase(object):
  """ Base class for a canvas -- used by pdpy.pdpy and pdpy.canvas """

  def __init__(self, obj_idx=0, isroot=False):
    """ Initialize the canvas base class """
    
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
