#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" PdPy file to Json-format file """

import re
import json
import ast

from ..classes.classes import PdObject
from ..util.utils import log

__all__ = [ "PdPyLoad" ]

def paren_matcher (n):
    # poor man's matched paren scanning, gives up
    # after n+1 levels.  Matches any string with balanced
    # parens inside; add the outer parens yourself if needed.
    # Nongreedy.
    return r"[^()]*?(?:\("*n+r"[^()]*?"+r"\)[^()]*?)*?"*n

def PdPyLoad(fp, patch, pddb):
  """ Reads the lines from a .pdpy file pointer `fp` and populates a `PdPy` obj
  
  Returns
  -------
  A PdPy patch objects

  Input
  -----
  1. `.pdpy` file pointer `fp`
  2. patch object (`PdPy`) to load 
  3. `pddb` is a json file holding a pure data object database

  """
  f = fp.read() # .replace('\n','')
  # print(repr(f))

  def getparens(s):
    result = re.findall(r"\((.*)\)", s, re.DOTALL)
    if result:
      if '(' in result[-1] or ')' in result[-1]:
        result.append(getparens(result[-1]))
      return result
  # print(getparens(f))

  matches = []
  def getmatch(s):
    match = re.search(r"\((.*)\)", s, re.DOTALL)
    if match:
      print(match)
      matches.append(match)
      match = getmatch(s[match.start()+1:match.end()-1])
  
  def getContectWithinBraces( x , *args , **kwargs):
    ptn = r'[%(left)s]([^%(left)s%(right)s]*)[%(right)s]' %kwargs
    Res = []
    res = re.findall(ptn , x)
    while res != []:
        Res = Res + res
        xx = x.replace('(%s)' %Res[-1] , '%s')
        res = re.findall(ptn, xx)
        # print(res)
        if res != []:
            res[0] = res[0] %('(%s)' %Res[-1])
    return Res

  # getmatch(f)
  # matches = getContectWithinBraces(f , left='\(\[\{' , right = '\)\]\}')
  # for i,m in enumerate(matches):
    # print(i,repr(m))
  # p
    # r"[^()]*?",
    # r"\)[^()]*?)*?"


  def depthStack(string):
    canvases = {}
    depth=-1
    for i,s in enumerate(string):
      prevdepth = depth
      if s == "(":
        depth += 1
        if prevdepth in canvases:
          canvases[prevdepth] += f"[{depth}]"
      elif s == ")":
        depth -= 1
        if prevdepth in canvases:
          canvases[prevdepth] += f"[{depth}]"
      else:
        if depth in canvases:
          canvases[depth] += s
        else:
          canvases.update({depth:s})
    return canvases
  
  # print(json.dumps(depthStack(f),indent=4))



  matches = []
  def depthfirst(string):
    outermost = re.findall(r"\((.*)\)", string, re.DOTALL)
    if outermost:
      for o in outermost:
        m = depthfirst(o)
        if m:
          matches.append(m)
      return outermost
    # if match:
      # return depthfirst(string[match.start()+1:match.end()-1])
    
    # for s in string:
    #   left = 0
    #   right = 0
    #   if s == "(":
    #     left += 1
    #   elif s == ")":
    #     right += 1
    #   if left == right:
    #     match = True
    #   else:


    # return canvases
  
  # vs = depthfirst(f)
  # for i,e in enumerate(matches):
    # print(i, repr(e))
  # print(json.dumps(vs,separators=(",",":")))

  # depth = -1
  # for i,s in enumerate(f):
  #   prevdepth = depth
  #   if s == "(":
  #     depth += 1
  #     prevdepth = depth
  #   elif s == ")":
  #     depth -= 1
  #     prevdepth = depth
  #   if prevdepth != depth:
  #     vs.update({depth:[]})
  #   vs.append([depth,s])
  matches = []
  def getparens(string):
    left = 0
    right = 0
    last_left_idx = 0
    last_right_idx = 0
    for i,s in enumerate(string):
      if '(' == s:
        left += 1
        last_left_idx = i+1
      elif ')' == s:
        right += 1
        left -= 1
        last_right_idx = i
      
      # print("match",left,right,last_left_idx,last_right_idx)
      if left == right and last_left_idx != last_right_idx:
        return {
            "content": string[last_left_idx:last_right_idx],
            "start":last_left_idx,
            "end":last_right_idx
          }
    
  # print(getparens(f))


  # print(ast.dump(ast.parse(f,mode='eval'),indent=4))
  newstring = []

  def getAll(string):
    match = getparens(string)
    if match:
      newstring.append(match['content'])
      remain = string[:match['start']-1] + string[match['end']+1:]
      if remain:
        getAll(remain)

  # getAll(f)
  
  # for i,m in enumerate(newstring):
    # print(i,repr(m))
  
  class canvas:
    def __init__(self, nodes):
      self.nodes = nodes
  

  canvases = []
  depth = -1
  for s in f:
    if s == '(':
      depth += 1
      canvases.append(canvas(''))

    elif s == ")":
      depth -= 1
      canvases[depth]
    else:
      canvases[-1].nodes += s

  for i,m in enumerate(canvases):
    print(i,repr(m))




  # return patch