#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
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
               default=None):
    """ Takes in a send and receive symbol pair or a json dict """
    self.__pdpy__ = self.__class__.__name__
    super().__init__(json=json, xml=xml)
    if default is None:
      default = self.__d__.iemgui['symbol']
    if json is None and xml is None:
      self.send = send if send is not None else default
      self.receive = receive if receive is not None else default
    
  def __pd__(self, order=0):
    """ Returns a pd string for this send/receive pair"""
    if order==1:
      return f"{self.receive} {self.send}"
    else:
      if hasattr(self, 'send') and self.send is not False:
        return f"{self.send} {self.receive}"
      else:
        return f"{self.receive}"

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
  
  def __remap__(self, obj_map):
    """ Get the value from the mapped indices """
    s = '-1'
    try:
      # query the map for the value at the id key
      s = str( obj_map[int(self.id)] )
    except KeyError:
      # if the key is not found, log the error
      log(1, "__remap__()::Key Not Found", self.id)
      print(obj_map)
    finally:
      # return the value
      return s

  def __pd__(self, obj_map=None):
    return f"{self.__remap__(obj_map) if obj_map else self.id} {self.port}"
  
  def __xml__(self, obj_map=None, tag=None):
    """ Returns an xml element for this source """
    x = super().__element__(scope=self, tag=tag)
    super().__subelement__(x, 'id', text = self.id)
    super().__subelement__(x, 'port', text = self.port)
    return x

class Edge(Base):
  """ A Pd Connection 
  Description
  -----------
  A Pd Connection object is a connection between two objects.

  Parameters
  ----------
  1. `source`: The source id of the connection
  2. `port`: The port outlet of the source
  3. `target`: The target id of the connection
  4. `port`: The port inlet of the target
  """
  def __init__(self, pd=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(cls="connect", json=json, xml=xml)
    if pd is not None and json is None and xml is None:
      self.source = Source(id=pd[0], port=pd[1]) 
      self.sink = Source(id=pd[2], port=pd[3])

  def __pd__(self, o=None):
    return super().__pd__(f"{self.source.__pd__(o)} {self.sink.__pd__(o)}")

  def __xml__(self, o=None):
    """ Returns an xml element for this edge """
    x = super().__element__(self)
    super().__subelement__(x, self.source.__xml__(o, tag='source'))
    super().__subelement__(x, self.sink.__xml__(o, tag='sink'))
    return x
