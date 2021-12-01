#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
               default=None):
    """ Takes in a send and receive symbol pair or a json dict """
    self.__pdpy__ = self.__class__.__name__
    super().__init__()
    if default is None:
      default = self.__d__.iemgui['symbol']
    if json is not None:
      super().__init__(json=json)
    else:
      self.send = send if send is not None else default
      self.receive = receive if receive is not None else default
    
  def __pd__(self, order=0):
    """ Returns a pd string for this send/receive pair"""
    if order==1:
      return f"{self.receive} {self.send}"
    else:
      if self.send is not False:
        return f"{self.send} {self.receive}"
      else:
        return f"{self.receive}"

class Source(Base):
  def __init__(self, id=None, port=None, json=None, xml=None):
    self.__pdpy__ = self.__class__.__name__
    if id is not None and port is not None:
      self.id = id
      self.port = port
    elif json is not None:
      super().__populate__(self, json)
    elif xml is not None:
      self.id = xml.findtext('id', None)
      self.port = xml.findtext('port', None)
    else:
      raise ValueError(f"{self.__pdpy__}: No valid parameters given")
  
  def remap(self, obj_map):
    """ Get the value from the mapped indices """
    s = '-1'
    try:
      # query the map for the value at the id key
      s = str( obj_map[int(self.id)] )
    except KeyError:
      # if the key is not found, log the error
      log(1, "remap()::Key Not Found", self.id)
      print(obj_map)
    finally:
      # return the value
      return s

  def __pd__(self, obj_map=None):
    return f"{self.remap(obj_map) if obj_map else self.id} {self.port}"

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
    super().__init__(cls="connect")
    if pd is not None:
      self.source = Source(id=pd[0], port=pd[1]) 
      self.sink = Source(id=pd[2], port=pd[3])
    elif json is not None:
      super().__populate__(self, json)
    elif xml is not None:
      self.source = Source(xml=xml.find('source', None))
      self.sink = Source(xml=xml.find('sink', None))
    else:
      raise ValueError(f"{self.__pdpy__}: No valid parameters given")

  def __pd__(self, o=None):
    return super().__pd__(f"{self.source.__pd__(o)} {self.sink.__pd__(o)}")