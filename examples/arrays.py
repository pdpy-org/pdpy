#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
import pdpy
with pdpy.PdPy(name='arrays', root=True) as pd:
  for _ in range(3):
    pd.createArray()
  pd.createArray(name="myarray", length=123)
  pd.createArray(name="keeping", length=100, keep=True, data=[1/i**2 for i in range(-50,50) if i != 0])
  pd.createGOPArray()