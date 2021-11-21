#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

from .base import Base

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
               json_dict=None,
               default=None):
    """ Takes in a send and receive symbol pair or a json dict """
    self.__pdpy__ = self.__class__.__name__
    super().__init__()
    if default is None:
      default = self.__d__.iemgui['symbol']
    if json_dict is not None:
      super().__init__(json_dict=json_dict)
    else:
      self.send = send if send is not None else default
      self.receive = receive if receive is not None else default
    
  def __pd__(self, order=0):
    """ Returns a pd string for this send/receive pair"""
    if order==1:
      return f"{self.receive} {self.send}"
    else:
      return f"{self.send if self.send != False else ''} {self.receive}"

class Source(Base):
  def __init__(self, id=None, port=None, json_dict=None, xml_object=None):
    self.__pdpy__ = self.__class__.__name__
    if id is not None and port is not None:
      self.id = id
      self.port = port
    elif json_dict is not None:
      super().__populate__(self, json_dict)
    elif xml_object is not None:
      self.id = xml_object.findtext('id', None)
      self.port = xml_object.findtext('port', None)
    else:
      raise ValueError(f"{self.__pdpy__}: No valid parameters given")

  def __pd__(self):
    return f"{self.id} {self.port}"

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
  def __init__(self, pd=None, json_dict=None, xml_object=None):
    self.__pdpy__ = self.__class__.__name__
    super().__init__(cls="connect")
    if pd is not None:
      self.source = Source(id=pd[0], port=pd[1]) 
      self.sink = Source(id=pd[2], port=pd[3])
    elif json_dict is not None:
      super().__populate__(self, json_dict)
    elif xml_object is not None:
      self.source = Source(xml_object=xml_object.find('source', None))
      self.sink = Source(xml_object=xml_object.find('sink', None))
    else:
      raise ValueError(f"{self.__pdpy__}: No valid parameters given")

  def __pd__(self):
    return super().__pd__(f"{self.source.__pd__()} {self.sink.__pd__()}")