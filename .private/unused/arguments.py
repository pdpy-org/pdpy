#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Arguments Class Definitions """

__all__ = [
  "Arguments"
]

class Arguments:
  """ Arguments Class
  
  Description
  -----------
  This class represents a list of arguments for a Pd object.
  """
  def __init__(self, args=None):
    """ Initialize with a list of arguments """
    self.__pdpy__ = self.__class__.__name__

    if args is not None:
      self.args = args
    else:
      self.args = []
  
  def __pd__(self):
    """ Parses the arguments into a string """
    s = ""
    for x in self.args:
      s += f" {x}"
    return s
  
  def __repr__(self):
    """ Returns a string representation of the arguments """
    return self.__pd__()
  
  def __str__(self):
    """ Returns a string representation of the arguments """
    return self.__pd__()
  
  def __len__(self):
    """ Returns the length of the arguments """
    return len(self.args)
  
  def __getitem__(self, key):
    """ Returns the argument at the specified index """
    return self.args[key]
  
  def __setitem__(self, key, value):
    """ Sets the argument at the specified index """
    self.args[key] = value
  
  def __delitem__(self, key):
    """ Deletes the argument at the specified index """
    del self.args[key]
  
  def __iter__(self):
    """ Returns an iterator for the arguments """
    return iter(self.args)
  
  def __contains__(self, item):
    """ Returns true if the argument is in the list """
    return item in self.args
  
  def __add__(self, args):
    """ Adds the arguments to the list """
    if not hasattr(self, 'args'):
      self.args = []
    
    if not isinstance(args, list):
      args = [args]
    
    for arg in args:
      self.args += arg
    
    return self
  