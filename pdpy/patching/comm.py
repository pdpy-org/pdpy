#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Class Definitions """

from ..core.base import Base

__all__ = [ 'Comm' ]

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
