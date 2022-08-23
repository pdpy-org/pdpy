#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
from pdpy import PdPy, Obj                  # necessary imports
offset = 110                                # fundamental frequency in Hz 
partials = 8                                # number of partials
mypatch = PdPy(name="additive_env", root=True)  # initialize a patch
dac = Obj('dac~')                           # instantiate a ``dac~`` object
mypatch.create(dac)                         # creates the dac within the canvas
# make a power envelope
phasor = Obj('phasor~').addargs(-0.5)       # create a phasor at freq -0.5 Hz
multiplier = Obj('*~')                      # to change to power
lopass = Obj('lop~').addargs(100)           # a lopass filter to smooth a bit
mypatch.create(phasor, multiplier, lopass)  # create the three
mypatch.connect(phasor, [multiplier,0,1])   # ``phasor~`` to 2 inlets of ``*~``
mypatch.connect(multiplier, lopass)         # ``*~`` to ``lop~``
for i in range(1, partials):                # loop through all partials
  objects = [                               # put objects on a list
    Obj("osc~").addargs(offset * i),        # a sinusoid at the partial's freq
    Obj("*~").addargs(1 / partials),        # brute normalization
    Obj("*~")
  ]
  mypatch.create(*objects)                  # create the objects list
  mypatch.connect(*objects)                 # connect it
  mypatch.connect(lopass, [objects[-1], 1]) # multiply by envelope 
  mypatch.connect(objects[-1], [dac, 0, 1]) # connect ``*~`` to dac chans 1,2
mypatch.write("additive_env.json")          # write the patch out
mypatch.write()                             # write the patch out