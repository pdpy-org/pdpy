#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
from pdpy import PdPy, Obj
from math import factorial, pow, exp, cos

def poisson(k, l=6): 
  return ( pow(l, k) / factorial(k) ) * exp(-k)

# initialize a patch (ie, a pdpy root patch)
mypatch = PdPy(name="additive", root=True)
# initialize an oscillator, a range and a dac with 4 channels
partials = 10

def makephasors(i):
  coef = poisson(i)/partials
  objects = [
    Obj('phasor~').addargs(coef * 10, cos(coef)),
    Obj('*~').addargs(coef * 50),
    Obj('+~').addargs(coef * 800),
    Obj('osc~'),
    Obj('*~').addargs(coef)
  ]
  mypatch.create(*objects)
  mypatch.connect(*objects)
  mypatch.connect(objects[-1], [dac, 0, 1])

dac = Obj('dac~')
mypatch.create(dac)

for i in range(partials):
  makephasors(i)

# write out the patch
mypatch.write()