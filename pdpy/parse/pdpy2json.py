#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" PdPy file to Json-format file """

import re

from ..utilities.utils import log, printer
from ..objects.obj import Obj

__all__ = [ 'PdPyLoad' ]

@printer
def is_ignored(s): 
  """ Ignore out-of-patch comments
  """
  return bool(re.search(r"^/\*.*$", s)    or 
              re.search(r"^\s\*.*$", s) or 
              re.search(r"^\*/$", s)    or 
              re.search(r"^[\s]*//", s) or 
              re.search(r"^\n", s))

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
  canvases = []

  @printer
  def is_root(s):
    """ Root canvas opening parens
    """
    if re.search(r"^\(.*$",s):
      name = re.findall(r"^\(#(.*)$", s)
      if bool(name):
        log(0,"NAME", name)
        root = patch.pdpyRoot(name=" ".join(name).strip())
      else:
        root = patch.pdpyRoot()
      canvases.append(root)
      return True

  @printer
  def is_root_end(s):
    """ Root canvas closing parens (ignores root canvas restore)
    """
    if re.search(r"^\).*$",s):
      canvases.pop()
      return True
  
  @printer
  def is_subpatch(s):
    """ Create Pd Canvases
    """
    if re.search(r"^\s+\(.*$",s):
      name = re.findall(r"^\s+\(#(.*)$",s)
      if bool(name):
        cnv = patch.pdpyCanvas(name=" ".join(name).strip().replace(' ','\ '))
      else:
        cnv = patch.pdpyCanvas()
      canvases.append(cnv)
      return True

  @printer
  def is_subpatch_end(s):
    """ Ends a subpatch (calls restore and pipes args after parens)
    """
    if re.search(r"^\s+\).*$",s):
      piped = re.findall(r"^\s+\)(.*)$",s)
      # check first if pipe is present and pass an outlet
      if bool(piped):
        if 'outlet' not in canvases[-1].nodes:
          prev = patch.__last_canvas__().__obj_idx__
          last = patch.objectCreator(Obj, ('outlet'))
        patch.objectConnector(prev,last.id)
      # restore the canvas
      patch.pdpyRestore()
      # check again and pass arguments to pipe through
      if bool(piped):
        string = " ".join(piped).strip()
        # string = 
        if bool(string):
          patch.pdpyCreate(' '*len(canvases)*2 + string,pddb)
        # parsePdPyLine(' ' * len(canvases)*2 + " ".join(piped).strip())
        # patch.objectConnector()
      # clear the canvas out of the stack
      canvases.pop()
      return True
  
  @printer
  def is_pdtext(s):
    """ Adds a pure data in-patch comment to the canvas
    """
    if re.search(r"^\s+[#+].+$", s):
      comment = re.findall(r"^\s+[#+](.+)$", s) 
      if bool(comment):
        patch.pdpyComment(" ".join(comment).strip())
      return True

  @printer
  def is_pdobj(s):
    """ Any object creator on the pd canvas
    """
    if re.search(r"^\s+[\*\w\d\\\-%].+$", s): 
      objects = re.findall(r"^\s+([\*\w\d\\\-%].+)$", s) 
      if bool(objects):
        print("obj",objects)
        patch.pdpyCreate(" ".join(objects).strip(), pddb)
      return True

  def parsePdPyLine(s):
    """ PdPy line parsing dispatcher
    """
    # print("-"*30)
    # print(repr(s))
    # print("-"*30)
    if is_ignored(s): return
    if is_root(s): return
    if is_root_end(s): return
    if is_subpatch(s): return
    if is_subpatch_end(s): return
    if is_pdtext(s): return    
    if is_pdobj(s): return
    # log(1,"parsePdPyLine: Unparsed Lines:", repr(s))
  
  for line_number, s in enumerate(fp.readlines()):
    # print("="*80)
    # print(f"Line Number : {line_number+1}: {repr(s)}")
    parsePdPyLine(s)

  return patch
