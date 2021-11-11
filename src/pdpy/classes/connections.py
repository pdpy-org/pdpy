#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

from .base import Base

__all__ = [ 
  'Edge',
  'Source'
]

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
    if pd is not None:
      self.source = Source(id=pd[0], port=pd[1]) 
      self.sink = Source(id=pd[2], port=pd[3])
    elif json_dict is not None:
      super().__populate__(self, json_dict)
    elif xml_object is not None:
      self.source = Source(xml_object.find('source', None))
      self.sink = Source(xml_object.find('sink', None))
    else:
      raise ValueError(f"{self.__pdpy__}: No valid parameters given")
