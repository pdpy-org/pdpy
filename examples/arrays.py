#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
import pdpy
import math
with pdpy.PdPy(name='arrays', root=True) as pd:
  for _ in range(3):
    pd.createArray()
  pd.createArray(name="myarray", length=123)
  sinewave = [ math.cos( i / 100 * 2 * math.pi) for i in range(100) ]
  pd.createArray(name="keeping", length=100, keep=True, data=sinewave)
  pd.createGOPArray(data = map(lambda x,y: x * y**2, sinewave, sinewave))