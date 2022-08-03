#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
from pdpy import PdPy, Obj
from math import factorial, pow, exp, cos
import random

def poisson(k, l=6): 
  return ( pow(l, k) / factorial(k) ) * exp(-k)

# initialize a patch (ie, a pdpy root patch)
pd = PdPy(name="additive", root=True)

partials = 25

dac = Obj('dac~')
pd.create(dac)

for i in range(1, partials):
  p = poisson(i) / partials
  rand = random.random()
  objects = [
    Obj('phasor~').addargs(p * 10, cos(p)),
    Obj('lop~').addargs(100),
    Obj('*~').addargs(p * 800),
    Obj('+~').addargs(p * 800 + 500),
    # phased out oscillators
    Obj('phasor~'),
    Obj('+~').addargs(cos(1-p)),
    Obj('cos~'),
    # add here some tiny waveshaping 
    Obj('*~').addargs(2),
    Obj('-~').addargs(1),
    Obj('clip~').addargs(-0.3, 0.3),
    Obj('*~').addargs(p),
    Obj('*~'),
    Obj('*~').addargs(1-rand),
    Obj('*~').addargs(rand)
  ]
  pd.create(*objects)
  pd.connect(*objects[:-2])
  # add an envelope triggered by the 1st phasor (1-phasor)
  oneminus = [
    Obj('sig~').addargs(1),
    Obj('-~')
  ]
  pd.create(*oneminus)
  pd.connect(*oneminus)
  # make it a quartic envelope
  # using a convoluted programmatical way:
  #
  prev_m = Obj('*~')
  pd.create(prev_m)
  pd.connect(objects[1], [prev_m, 0, 1])
  for x in range(4):
    next_m = Obj('*~')
    pd.create(next_m)
    pd.connect(prev_m, [next_m, 0, 1])
    prev_m = next_m
  pd.connect(prev_m, [oneminus[-1], 1])
  
  # or this direct way:
  # 
  # mul = Obj('*~')
  # mul2 = Obj('*~')
  # pd.create(mul, mul2)
  # pd.connect(objects[1], [mul, 0, 1])
  # pd.connect(mul, [mul2, 0, 1])
  # pd.connect(mul2, [oneminus[-1], 1])

  pd.connect(oneminus[-1], [objects[-3], 1]) 
  # plug it to the dac, in stereo
  pd.connect(objects[-3], objects[-2])
  pd.connect(objects[-3], objects[-1])
  pd.connect(objects[-1], [dac, 0])
  pd.connect(objects[-2], [dac, 1])

# write out the patch
pd.write()