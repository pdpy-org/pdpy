#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021-22 Fede Camara Halac
# **************************************************************************** #
""" 
Msg
===
"""

from ..core.object import Object
from ..core.message import Message

__all__ = [ 'Msg' ]

class Msg(Object):
  """ Representation of a patchable Pd Message box

  This class represents a Pd message box with a list of targets.
  Each ``target`` is an instance of :class:`Message`.

  Parameters
  ----------

  message : :class:`str`, a :class:`list` of :class:`str`, or ``None``
    A string or a list of strings with a message. 
    Each element of the list defaults to the ``outlet`` target.
  
  pd_lines : :class:`str`
    A pd-lang string with a message, eg: ``#X msg 10 10 Hello world``
    Or, for multiple targets: ``#X msg 10 10 Hello World \\;pd quit``
  
  json : :class:`dict`
    A json dictionary with the scope of a Msg.
  
  """
  def __init__(self, message=None, pd_lines=None, json=None):

    self.__pdpy__ = self.__class__.__name__
    super().__init__(cls='msg',json=json)

    if json is None and pd_lines is not None:
      super().__init__(*pd_lines[:3], cls='msg')
      self.className = self.__cls__
      argv = pd_lines[3:]
      if len(pd_lines[3:]):
        self.addMessages(argv)
    
    if message is not None:
      self.addMessages([message] if not isinstance(message, list) else message)
      
  def addTarget(self, address=None):
    """ Add a target to the message target list
    """
    if not hasattr(self, "targets"):
      self.targets = []
    target = Message(address=address)
    self.targets.append(target)
    return target


  def addMessages(self, argv):
    """ Add a new message to its appropriate ``target`` """
    
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

      return self

  def __pd__(self):
    """ Return the pd-lang string for this message """
    s = ''
    for target in getattr(self, "targets", []):
      s += target.__pd__()
    
    if hasattr(self, "border"):
      s += f', f {self.border}'
    
    return super().__pd__(s) if s else ''
  
  def __xml__(self):
    """ Return the XML Element for this message """
    x = super().__xml__(scope=self, tag=self.__cls__, attrib='border')
    
    if hasattr(self, 'targets'):
      targets = super().__element__(tag='targets')
      for target in getattr(self, "targets", []):
        super().__subelement__(targets, target.__xml__())
      super().__subelement__(x, targets)

    return x
