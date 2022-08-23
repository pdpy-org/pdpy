#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" PdPy file to Json-format file """

# get the first command line argument as the input file
import json
import sys

def execute(argv):
  print("PdPy file to Json-format file", argv)
  args = []
  for arg in argv:
    if str(arg).startswith('#'):
      continue
    args.append(arg)
  return " ".join(args)

input_file = sys.argv[1]

# open the file and read it as a string
with open(input_file, 'r') as f:
    data = f.read()

depth = 0
canvases = {}
canvas = []
line = ''

# iterate over the string
for s in data:
  # on opening parenthesis increase the depth
  if s == '(':
    # case 0: we are at the root
    if depth == 0 and canvas != []:
      canvases.update({depth: execute(canvas)})
      canvas = []
    depth += 1
  # on closing parenthesis decrease the depth
  elif s == ')':
    # we can parse an expression...
    if canvas != []:
      depth -= 1 # relocate to the previous level
      if depth in canvases:
        cnv = canvases[depth] # get the previous canvas
        cnv += execute(canvas)
      else:
        canvases.update({depth: execute(canvas)})
      canvas = []

    
    # uncomment to stack the expression on the appropriate level
    # # check we have content
    # if canvas != []:
    #   if depth in canvases:
    #     cnv = canvases[depth] # the previous canvas
    #     cnv += canvas
    #   else:
    #     canvases.update({depth: canvas})
    #   canvas = [] # reset the content
    # depth -= 1
  
  # neither, we need to update content
  else:
    if s == '\n' and line != '':
      # remove unnecesary space
      line = line.strip()
      if line != '':
        canvas.append(line)
        line = ''
    else:
      line += s
print(data.replace('\n', '').replace(' ', ''))
print(json.dumps(canvases, indent=2))