#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

from .base import Base
from .classes import Point

__all__ = [ "PdMessage" ]

class PdMsg(Base):
  def __init__(self, address):
    self.__pdpy__ = self.__class__.__name__
    self.address = address
  
  def add(self, msg):
    if not hasattr(self, "message"):
      self.message = []
    self.message.append(msg)

class PdMessage(Base):
  def __init__(self, id, x, y, *argv):
    self.__pdpy__ = self.__class__.__name__
    self.className = "msg"
    self.position = Point(x, y)
    self.id = int(id)
    argc = len(argv)
    argv = list(argv)
    
    if argc:
      
        if 2 < len(argv) and "f" == argv[-2] and argv[-1].isnumeric():
          self.border = self.num(argv[-1])
          argv = argv[:-2]
          argv[-1] = argv[-1].replace(",","")
      

        if len(argv) >= 1:
          self.targets = []
          self.targets.append(PdMsg("outlet"))
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
    
  def addTarget(self, target):
    if not hasattr(self, "targets"):
      self.targets = []
    self.targets.append(PdMsg(target))  
