#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" PdPy file to Json-format file """

import re
from ..util.utils import log

__all__ = [ "PdPyLoad" ]

def p(t, s=None): print(t,repr(s.strip())) if s is not None else print(t)

multicomment = {
  "begin" : re.compile(r"^/\*.*$"),
  "end"   : re.compile(r"^\s\*/$")
}

def PdPyLoad(fp, patch, i):
  depth = -1
  in_comment = False
  for s in fp.readlines():
    print("PdPyLoad",repr(s))
    
    if in_comment: continue
    
    if re.search(multicomment['begin'], s) :    
      p("BEGIN-comment") 
      in_comment = True
      continue
    
    if re.search(multicomment['end'], s) :    
      p("END-Comment")   
      in_comment = False
      continue 


    if re.search(r"^\(.*$",s):
      print("CANVAS",repr(s))
      canvas_name = ''
      if depth == -1: patch.createRoot(name=canvas_name)
      else: patch.createCanvas(name=canvas_name)
      depth += 1
    elif re.search(r"^ +\)$",s):
      print("RESTORE",repr(s))
      if depth: patch.restore() # patch coords # patch connections
    elif re.search(r"^\s+[\*\w\d\\\-\&%].+$", s):
      print("OBJECT",repr(s))
      argv = s
      patch.pdpyCreate(argv, i)
    elif re.search(r"^\s+[#+].+",s):
      print("TEXT",repr(s))
      comment = re.findall(r"^\s+[#+](.+)$",s)
      patch.pdpyComment(comment)
    # elif re.search(r"^\s{4}\)$",s):   patch.restore()
    # elif re.search(r"^\)$",s):        patch.restore()
    # elif re.search(r"^\(#.*$",s): patch.createRoot(name=s[2:])
    # elif re.search(r"^\s{2}\($",s):    patch.createCanvas()
    # elif re.search(r"^\s{4}\($",s):    patch.createCanvas()
    # elif re.search(r"^\s{2}\(#.*$",s): patch.createCanvas(name=s[4:])
    # elif re.search(r"^\s{4}\(#.*$",s): patch.createCanvas(name=s[6:])
    # elif re.search(r"^\s{2}[\*\w\d\\\-%].+$", s): patch.pdpyCreate(s[2:],i)
    # elif re.search(r"^\s{2}\).*$",s):             patch.pdpyCreate(s[3:], i)
    # elif re.search(r"^\s{4}[\*\w\d\\\-%].+$", s): patch.pdpyCreate(s[4:],i)
    # elif re.search(r"^\s{4}\).*$",s):             patch.pdpyCreate(s[5:], i)
    # elif re.search(r"^\s{6}[\*\w\d\\\-%].+$", s): patch.pdpyCreate(s[6:],i)
    # elif re.search(r"^\s{2}[#+].+$", s): patch.pdpyComment(s[3:].strip())
    # elif re.search(r"^\s{4}[#+].+$", s): patch.pdpyComment(s[5:].strip())
    # elif re.search(r"^\s{6}[#+].+$", s): patch.pdpyComment(s[6:].strip())
    
    elif re.search(r"^[\s]*//", s):  
      p("Comment", s[2:]) 
      continue
    elif re.search(r"\n", s):
      continue
    else:
      print("UNKNOWN", repr(s))
  return patch
