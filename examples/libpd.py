#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
"""
Patcher
=======
"""

from pdpy_lib import Patch, Obj

with Patch(name="mypatch", root=True) as p:
  osc = [Obj('osc~').addargs(110 * i) for i in range(1, 16)]
  mul = Obj('*~').addargs(1/16)
  dac = Obj('dac~')
  p.create(*osc, dac, mul)
  for o in osc: p.connect(o, mul)
  p.connect(mul, [dac, 0, 1])