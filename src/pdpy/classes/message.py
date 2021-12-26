#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Class Definitions """

from pdpy.util.utils import log
from .base import Base
from .pdobj import PdObj

__all__ = [
  'PdMessage',
  'PdMsg'
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
  def __init__(self, address=None, json=None, xml=None):
    """ Initialize with a address or default to 'outlet' """
    self.__pdpy__ = self.__class__.__name__
    super().__init__(json=json, xml=xml)
    if json is None and xml is None:
      if address is not None:
        self.address = address
      else:
        self.address = 'outlet'
    # log(0, self.address, 'initialized.')
  
  def add(self, msg):
    if not hasattr(self, 'message'):
      self.message = []
    msg = " ".join(msg) if isinstance(msg, list) else msg
    # log(0, f'{self.address} -> adding message: {msg}')
    self.message.append(msg)

  def __pd__(self):
    """ 
    Returns a string of escaped comma-separated Pd messages or an empty string.
    If there is a address, output an escaped semicolon 
    and the address before the message
    """
    s = f' \; {self.address} ' if self.address != 'outlet' else ''
    if hasattr(self, 'message'):
      s += ' \, '.join(list(map(lambda x:str(x), self.message))) 

    return s

  def __xml__(self):
    """ Returns the XML Element for this object """
    x = super().__element__(self)
    super().__subelement__(x, 'address', text=self.address)
    if hasattr(self, 'message'):
      msg = super().__element__(tag='message')
      for m in getattr(self, 'message', []):
        super().__subelement__(msg, 'msg', text=m)
      super().__subelement__(x, msg)
    return x

class PdMessage(PdObj):
  """ Representation of a Pd Message box

  Description
  -----------
  This class represents a Pd message box with a list of targets
  each target being a ::class::`PdMsg` instance
  
  """
  def __init__(self, pd_lines=None, json=None):

    self.__pdpy__ = self.__class__.__name__
    super().__init__(cls='msg',json=json)

    if json is None and pd_lines is not None:
      super().__init__(*pd_lines[:3], cls='msg')
      self.className = self.__cls__
      argv = pd_lines[3:]
      if len(pd_lines[3:]):
        self.addMessages(argv)
      
  def addTarget(self, address=None):
    if not hasattr(self, "targets"):
      self.targets = []
    target = PdMsg(address=address)
    self.targets.append(target)
    return target


  def addMessages(self, argv):
    
    if 2 < len(argv) and "f" == argv[-2] and argv[-1].isnumeric():
      self.border = self.__num__(argv[-1])
      argv = argv[:-2]
      argv[-1] = argv[-1].replace(",","")

    # log(1, f'adding messages: {argv}')
    # parse the argument vector
    if len(argv) >= 1: # if there is at least one argument
      i = 0 # index of the current argument
      msgbuf = [] # buffer for the current message
      
      # add the first target
      last_target = None

      if "\\;" == argv[i]:
        if i + 1 < len(argv):
          i += 1
          last_target = self.addTarget(argv[i])
        i += 1
      else:
        last_target = self.addTarget()
      
      def _addmsg(msgbuf=msgbuf, target=last_target):
        # if the message buffer is not empty
        if len(msgbuf):
          # if there are targets,
          if target is not None:
            # add the message buffer to the last target
            target.add(msgbuf)
          else:
            # if there are no targets, add one and fill it with the message
            self.addTarget().add(msgbuf)
        return []
      
      
      # we will increment the index i until we reach the end of the arguments
      while i < len(argv):
        
        # if the current element is an escaped comma
        if "\\," == argv[i]:
          msgbuf = _addmsg(msgbuf) # add the message buffer to the last target
          i += 1
          continue
        
        # if the current element is an escaped semicolon, we have a new TARGET
        if "\\;" == argv[i]:
          msgbuf = _addmsg(msgbuf) # add the message buffer to the last target
          
          # special case for the first target
          # if i == 0:
            # last_target = self.addTarget()

          if i + 1 < len(argv):
            # the next element is the address
            i += 1
            if argv[i] != '': # if the address is not empty
              # add a new target with the address
              last_target = self.addTarget(argv[i]) 
          
          i += 1
          continue
        
        # if the current argument is neither escaped comma nor semi, 
        msgbuf.append(argv[i]) # add the current argument to the message buffer
        i += 1 # increment the index
      # end loop section while i < len(argv)
      # add the message if we still have 1 in the buffer
      msgbuf = _addmsg(msgbuf)

  def __pd__(self):
    """ Return a pd message in pd lang """
    s = ''
    for target in getattr(self, "targets", []):
      s += target.__pd__()
    
    if hasattr(self, "border"):
      s += f', f {self.border}'
    
    return super().__pd__(s) if s else ''
  
  def __xml__(self):
    """ Return the XML Element for this object """
    x = super().__xml__(scope=self, attrib=('border', 'className'))
    if hasattr(self, 'targets'):
      targets = super().__element__(tag='targets')
      for target in getattr(self, "targets", []):
        super().__subelement__(targets, target.__xml__())
      super().__subelement__(x, targets)
    return x
