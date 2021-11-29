#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

from .base import Base
from .pdobj import PdObj

__all__ = [
  "PdMessage",
  "PdMsg"
]

class PdMsg(Base):
  """ Representation of a Pd Message
  
  Description
  -----------
  This class represents a Pd message with a address symbol and a message list.
  If no address is given, the default is the 'outlet' symbol. This means that
  the message list needs to be outputted to the object's outlet. If a address
  is specified, then the list of messages is to be outputted to the address.

  Parameters
  ----------
  address : str (optional) - Default: 'outlet' 

  Attributes
  ----------
  address : str
    The address symbol name
  message : list
    The message list

  Methods
  -------
  add(msg) : None
    Add a message to the message list
  
  __pd__() : str
    Returns a string of escaped comma-separated Pd messages or an empty string
    This method outputs a semicolon if the address is not the default.

  """
  def __init__(self, address=None, json_dict=None):
    """ Initialize with a address or default to 'outlet' """
    self.__pdpy__ = self.__class__.__name__
    
    if json_dict is not None:
      super().__populate__(self, json_dict)
    else:
      if address is not None:
        self.address = address
      else:
        self.address = 'outlet'
  
  def add(self, msg):
    if not hasattr(self, 'message'):
      self.message = []
    self.message.append(msg)

  def __pd__(self):
    """ 
    Returns a string of escaped comma-separated Pd messages or an empty string.
    If there is a address, output an escaped semicolon 
    and the address before the message
    """
    s = f' \; {self.address} ' if self.address != 'outlet' else ''
    s += ' \, '.join(self.message) if hasattr(self, 'message') else ''
    return s

class PdMessage(PdObj):
  """ Representation of a Pd Message box

  Description
  -----------
  This class represents a Pd message box with a list of targets
  each target being a ::class::`PdMsg` instance
  
  """
  def __init__(self, pd_lines=None, json_dict=None):

    self.__pdpy__ = self.__class__.__name__

    if pd_lines is not None:
      super().__init__(*pd_lines[:3], cls='msg')
      self.className = self.__cls__
      argv = pd_lines[3:]
      if len(pd_lines[3:]):
        self.addMessages(argv)
    elif json_dict is not None:
      super().__init__(cls='msg',json_dict=json_dict)
      
  def addTarget(self, address):
    if not hasattr(self, "targets"):
      self.targets = []
    if isinstance(address, dict):
      self.targets.append(PdMsg(address['address'])) 
    else:
      self.targets.append(PdMsg(address))  

  def addMessages(self, argv):
      
    if 2 < len(argv) and "f" == argv[-2] and argv[-1].isnumeric():
      self.border = self.num(argv[-1])
      argv = argv[:-2]
      argv[-1] = argv[-1].replace(",","")
  
    if len(argv) >= 1:
      self.targets = []
      self.targets.append(PdMsg())
      i = 0
      msgbuf = ''
    
      while i < len(argv) :    
        if "\\," == argv[i]:
          if len(msgbuf) and len(self.targets):
            self.targets[-1].add(msgbuf)
            msgbuf = ''
          else:
            self.targets.pop()
          i += 1
          continue
        if "\\;" == argv[i]:
          if len(msgbuf) and len(self.targets):
            self.targets[-1].add(msgbuf)
            msgbuf = ''
          else:
            self.targets.pop()
          if i + 1 < len(argv):
            self.targets.append(PdMsg(argv[i+1]))
          i += 2
          continue
        if len(msgbuf):
          msgbuf += " " + argv[i]
        else:
          msgbuf = argv[i]
        i += 1
      
      if len(self.targets):
        self.targets[-1].add(msgbuf)

  def __pd__(self):
    """ Return a pd message in pd lang """
    s = ''
    for target in getattr(self, "targets", []):
      s += target.__pd__()
    
    if hasattr(self, "border"):
      s += f', f {self.border}'
    
    return super().__pd__(s) if s else ''
    