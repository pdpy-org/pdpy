#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
from pdpy import PdPy, Obj                  # necessary imports
offset = 110                                # fundamental frequency in Hz 
partials = 8                                # number of partials
mypatch = PdPy(name="additive", root=True)  # initialize a patch
dac = Obj('dac~')                           # instantiate a ``dac~`` object
mypatch.create(dac)                         # creates the dac within the canvas
for i in range(1, partials):                # loop through all partials
  objects = [                               # put objects on a list
    Obj("osc~").addargs(offset * i),        # a sinusoid at the partial's freq
    Obj("*~").addargs(1 / partials)         # brute normalization
  ]
  mypatch.create(*objects)                  # create the objects list
  mypatch.connect(*objects)                 # connect it
  mypatch.connect(objects[-1], [dac, 0, 1]) # connect ``*~`` to dac chans 1,2
mypatch.write()                             # write the patch out