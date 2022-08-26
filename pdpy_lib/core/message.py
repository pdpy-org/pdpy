#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021-22 Fede Camara Halac
# **************************************************************************** #
""" 
Message
=======
"""

from . import base

__all__ = [ 'Message' ]

class Message(base.Base):
  """ Representation of a Pd Message (non patchable, used by :class:`pdpy.Msg`)
  
  This class represents a Pd message.
  It stores a list of messages, together with a ``address``.
  If no address is given, the default is the outlet. 
  Otherwise, messages are sent to that address.

  Parameters
  ----------
  
  address : ``str`` or ``None``
    (optional) The target address of the message (default: ``"outlet"``)

  json : ``dict`` or ``None``
    (optional) A json dictionary with the scope of a Message
  
  xml : ``xml.etree.ElementTree.Element`` or ``None``
    (optional) An xml Element with the scope of a Message


  """
  def __init__(self, address=None, json=None, xml=None):
    # Initialize with a address or default to 'outlet'
    self.__pdpy__ = self.__class__.__name__
    super().__init__(json=json, xml=xml)
    if json is None and xml is None:
      if address is not None:
        self.address = address
      else:
        self.address = 'outlet'
    # log(0, self.address, 'initialized.')
  
  def add(self, msg):
    """ Add a message to the message list """
    if not hasattr(self, 'messages'):
      self.messages = []
    msg = " ".join(msg) if isinstance(msg, list) else msg
    # log(0, f'{self.address} -> adding messages: {msg}')
    self.messages.append(msg)

  def __pd__(self):
    """  Returns a string of escaped comma-separated Pd messages or an empty string.
    
    If there is a address, output an escaped semicolon 
    and the address before the message    
    """
    s = f' \; {self.address} ' if self.address != 'outlet' else ''
    if hasattr(self, 'messages'):
      s += ' \, '.join(list(map(lambda x:str(x), self.messages))) 

    return s

  def __xml__(self):
    """ Returns the XML Element for this object """
    x = super().__element__(scope=self, tag='message')
    super().__subelement__(x, 'address', text=self.address)
    if hasattr(self, 'messages'):
      msg = super().__element__(tag='messages')
      for m in getattr(self, 'messages', []):
        super().__subelement__(msg, 'm', text=m)
      super().__subelement__(x, msg)
    return x

