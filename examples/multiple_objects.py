#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
from pdpy import PdPy, Obj, Bng
# path to where the Pd-*.app exists
# pdpath = "/Users/fd/Development/pure-data"
pdpath = None
with PdPy(name="multiple_objects", root=True) as mypatch:
  for i in range(20):
    objects = [
      Bng(label=str(i), size=20),
      Obj('print').addargs(i),
      Obj('print').addargs(i)
    ]
    mypatch.create(*objects)
    mypatch.connect(objects[0], objects[1])