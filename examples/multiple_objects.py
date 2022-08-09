#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
from pdpy import PdPy, Obj, Bng
mypatch = PdPy(name='multiple_objects', root=True, pdpath="/Users/fd/Development/pure-data")
for i in range(25):
  objects = [
    Bng(label=str(i), size=20),
    Obj('print').addargs(i),
    Obj('print').addargs(i)
  ]
  mypatch.create(*objects)
  mypatch.connect(objects[0], objects[1])
  mypatch.connect(objects[0], objects[2])
# mypatch.write('multiple_objects.json')
mypatch.write()
mypatch.run()