#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
""" PdPy file to Json-format file """
import re
from .utils import printer

@printer
def is_ignored(line): 
  """ Check for out-of-patch comments
  """
  return bool(re.search(r"^/\*.*$", line)  or 
              re.search(r"^\s\*.*$", line) or 
              re.search(r"^\*/$", line)    or 
              re.search(r"^[\s]*//", line) or 
              re.search(r"^\n", line))

@printer
def is_root(line):
  """ Check for Root canvas opening parens and name
  """
  return re.search(r"^\(.*$",line), re.findall(r"^\(#(.*)$", line)

@printer
def is_subpatch(line):
  """ Check for Pd Sub Canvases and name (regex differs from is_root)
  """
  return re.search(r"^\s+\(.*$",line), re.findall(r"^\s+\(#(.*)$",line)

@printer
def is_root_end(line):
  """ Check for root canvas closing parens (ignores root canvas restore)
  """
  return re.search(r"^\).*$",line)

@printer
def is_pdtext(line):
  """ Checks for pure data in-patch comments
  """
  return re.findall(r"^\s+[#+](.+)$", line)

@printer
def is_piped(line):
  """ Gets all piped args after subpatch closing parens
  """
  return re.findall(r"^\s+\)(.*)$",line)

@printer
def is_subpatch_end(line):
  """ Ends a subpatch (calls restore and pipes args after parens)
  """
  return re.search(r"^\s+\).*$",line)

@printer
def is_pdobj(line):
  """ Any object creator on the pd canvas
  """
  return re.findall(r"^\s+([\*\w\d\\\-%\+\/].+)$", line)