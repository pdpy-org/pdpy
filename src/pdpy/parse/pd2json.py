#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Pure data file lines (spanning multiple rows) to Json file """

from ..util.utils import log
from ..classes.pddata import PdData

__all__ = [ "PureDataToJson" ]

def PureDataToJson(patch, pd_lines):

  store_graph = False
  last = None
  graph_candidate = 0
  i = 0
  
  for i in range(len(pd_lines)):
  
    nodes = pd_lines[i]
    # log(1, "NODES:", nodes)
    
    head = nodes[:2]
    body = nodes[2:]
    
    # either structs or canvases
    if "#N" == head[0]:
      if "struct" == head[1]:
        # struct element that exist on main canvas
        patch.addStruct(body)
      else:
        # the base canvas
        if 7 == len(nodes):
          graph_candidate = 0
          last = patch.addRoot(body)
        # canvas element: add a canvas node
        elif 8 == len(nodes):
          last = patch.addCanvas(body)
          graph_candidate += 1

    # saved array or text data
    elif "#A" == head[0]:
      if not str(head[1]).isnumeric():
        # text
        setattr(last, 'data', PdData(body, dtype=str, char=';',head=head[1]))
      else:
        # array, store as floats
        # last.size = body[0]
        setattr(last, 'data', PdData(body))
    # anything else is an "#X"
    else:
      # handle embedded declarations
      if "declare" == head[1]:
        patch.addDependencies(body)
      # the coords constructor
      elif "coords" == head[1]:
        graph_candidate += 1
        patch.addCoords(body)
      # restore constructor
      elif "restore" == head[1]:
        if "graph" == body[-1]:
          # log(1,"GRAPH", nodes)
          last = patch.restore(body)
        else:
          last = patch.restore(body)
      # border: This accounts for ',f [0-9]', ie., box field position line
      elif "f" == head[1]:
        setattr(last, "border", int(body[0]))
      # connection or edges
      elif "connect" in head[1]:
        patch.addConnection(body)
      # the ye-olde array ancestor
      elif "graph" in head[1]:
        last = patch.addGraph(body)
        store_graph = True
      # pop the array old
      elif "pop" == head[1]:
        store_graph = False
      # fill the array old
      elif "array" == head[1]:
        # check if we are in a graph
        if store_graph:
          last.addArray(head[1], body[1])
        # we are a gop array
        else:  
          # what in the world is this?
          if "saved" == body[0]:
            log(1,"'Saved' flag", nodes)
          else:
            # the modern array object
            last = patch.addGOPArray(body)
      # a scalar object
      elif "scalar" == head[1]:
        last = patch.addScalar(body)
      # a comment non-object
      elif "text" == head[1]:
        last = patch.addComment(body)
      # a float object
      elif "floatatom" == head[1]:
        last = patch.addNativeGui(head[1], body)
      # a symbol object
      elif "symbolatom" == head[1]:
        last = patch.addNativeGui(head[1], body)
      # a listbox object
      elif "listbox" == head[1]:
        last = patch.addNativeGui(head[1], body)
      # a message object
      elif "msg" == head[1]:
        last = patch.addMsg(body)
      # all other 'obj' constructors
      elif "obj" == head[1]:
        last = patch.addObj(body)
      else:
        log(1,"What is this?", nodes, patch.patchname)
