#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Json-formatted file (Python Patch Object) to Pure data file """

from .getters import *

__all__ = [ "PdPyToPureData" ]

name = ''

def PdPyToPureData(o):

  global name
  name = o.patchname  
  out = []

  if hasattr(o, "root"):
    # print(o.toJSON())
    # add structs
    getStruct(o, out)
    # add main root canvas
    getCanvas(o.root, out, root=True)
    # add declarations
    getDependencies(o, out)
    # add nodes
    getNodes(o.root, out)
    # add comments
    getComments(o.root, out)
    # add coords
    getCoords(o.root, out)
    # add connections
    getConnections(o.root, out)
    # add restore (if gop)
    getRestore(o.root, out)
  
  return "".join(out)
