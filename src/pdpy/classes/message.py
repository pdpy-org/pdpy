#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

import json
from .base import Base
from .classes import Point

__all__ = [
  "PdMessage",
  "PdMsg"
]

class PdMsg(Base):
  def __init__(self, json_dict=None):
    self.__pdpy__ = self.__class__.__name__
    if json_dict is not None:
      super().__populate__(self, json_dict)
  
  def add(self, msg):
    if not hasattr(self, "message"):
      self.message = []
    self.message.append(msg)

class PdMessage(Base):
  def __init__(self, pd_lines=None, json_dict=None):

    self.__pdpy__ = self.__class__.__name__
    super().__init__(cls="msg")

    if pd_lines is not None:
      self.className = self.__cls__
      self.id = int(pd_lines[0])
      self.position = Point(x=pd_lines[1], y=pd_lines[2])
      argv = pd_lines[3:]
      if len(pd_lines[3:]):
        self.addMessages(argv)
    elif json_dict is not None:
      super().__populate__(self, json_dict)
      # for k,v in json_dict.items():
      #   if 'targets' == k:
      #     for target in v:
      #       self.addTarget(target)
      #   setattr(self, k, v)
  
  def addTarget(self, target):
    if not hasattr(self, "targets"):
      self.targets = []
    if isinstance(target, dict):
      self.targets.append(PdMsg(json_dict=target))  
    else:
      self.targets.append(PdMsg(json_dict={'address':target}))  

  def addMessages(self, argv):
      
    if 2 < len(argv) and "f" == argv[-2] and argv[-1].isnumeric():
      self.border = self.num(argv[-1])
      argv = argv[:-2]
      argv[-1] = argv[-1].replace(",","")
  

    if len(argv) >= 1:
      self.targets = []
      self.targets.append(PdMsg(json_dict={'address':'outlet'}))
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
            self.targets.append(PdMsg(json_dict={'address':argv[i+1]}))
          i += 2
          continue

        if len(msgbuf):
          msgbuf += " " + argv[i]
        else:
          msgbuf = argv[i]
        
        i += 1
      
      if len(self.targets):
        self.targets[-1].add(msgbuf)
