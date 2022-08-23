#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Class Definitions """

from .base import Base
from pdpy.util.utils import log

__all__ = [
  'Comm',
  'Edge',
  'Source'
]

class Comm(Base):
  """
  Communication Class holding send and receive pairs
  """
  def __init__(self, 
               send=None,
               receive=None,
               json=None,
               xml=None,
               default=None, **kwargs):
    """ Takes in a send and receive symbol pair or a json dict """
    self.__pdpy__ = self.__class__.__name__
    super().__init__(json=json, xml=xml)
    if default is None:
      default = self.__d__.iemgui['label']
    if json is None and xml is None:
      self.send = send if send is not None else default
      self.receive = receive if receive is not None else default
    
  def __pd__(self, order=0):
    """ Returns a pd string for this send/receive pair"""
    if order==1:
      return str(self.receive) + " " + str(self.send)
    elif order==-1:
      return str(self.send) + " " + str(self.receive)
    else:
      if hasattr(self, 'send') and self.send is not False:
        return str(self.send) + " " + str(self.receive)
      else:
        return str(self.receive)

  def __xml__(self, order=0):
    """ Returns a XML Element for this send/receive pair"""
    if order==1:
      return super().__xml__(scope=self, attrib=('receive','send'))
    else:
      if hasattr(self, 'send') and self.send is not False:
        return super().__xml__(scope=self, attrib=('send','receive'))
      else:
        return super().__xml__(scope=self, attrib=('receive'))

class Source(Base):
  def __init__(self, id=None, port=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(json=json, xml=xml)
    if json is None and xml is None:
      self.id = id
      self.port = port
    # cast to int
    self.id = int(self.id)
    self.port = int(self.port)
  
  def setobj(self, parent):
    """ Locates the node in the parent (Canvas) object """
    for obj in getattr(parent, 'nodes', []):
      if getattr(obj, 'id') == self.id:
        setattr(self, '__obj__', obj) # update with a new attribute
    # log(1, f"setobj()::{self.__dict__}")
    

  def __remap__(self, obj_map):
    """ Get the value from the mapped indices """
    # query the map for the value at the id key
    if self.id in obj_map:
      return str(obj_map.get(self.id))
    else:
      log(1, "__remap__()::Key Not Found" + " " + str(self.id))
      return self.id

  def __pd__(self, obj_map=None):
    """ Returns a pd string for this source """
    if not hasattr(self, '__obj__'):
      return str(self.__remap__(obj_map) if obj_map else self.id)  + " " + str(self.port)
    else:
      return str(self.__obj__.id) + " " + str(self.port)
  
  def __xml__(self, obj_map=None, tag=None):
    """ Returns an xml element for this source """
    x = super().__element__(scope=self, tag=tag)
    super().__subelement__(x, 'id', text = self.id)
    super().__subelement__(x, 'port', text = self.port)
    return x

class Edge(Base):
  """ A Pd Connection 

  A Pd Connection object is a connection between two objects.

  Parameters
  ----------
  1. `source`: The source id of the connection
  2. `port`: The port outlet of the source
  3. `target`: The target id of the connection
  4. `port`: The port inlet of the target
  """
  def __init__(self, pd_lines=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(cls="connect", json=json, xml=xml)
    if pd_lines is not None and json is None and xml is None:
      self.source = Source(id=pd_lines[0], port=pd_lines[1]) 
      self.sink = Source(id=pd_lines[2], port=pd_lines[3])

  def connect(self):
    if not hasattr(self, '__p__'):
      log(1, "connect(): No parent Instance Attached")
    else:
      canvas = getattr(self,'__p__')
      # log(1, f"connect(): setting source")
      self.source.setobj(canvas)
      # log(1, f"connect(): setting sink")
      self.sink.setobj(canvas)
    return self

  def __pd__(self, o=None):
    # log(1,'EDGE to PD',self.__dict__)
    return super().__pd__(self.source.__pd__(o) + " " + self.sink.__pd__(o))

  def __xml__(self, o=None):
    """ Returns an xml element for this edge """
    x = super().__element__(scope=self)
    super().__subelement__(x, self.source.__xml__(o, tag='source'))
    super().__subelement__(x, self.sink.__xml__(o, tag='sink'))
    return x
