#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
from pdpy import PdPy, Obj, Msg
# initialize a patch (ie, a pdpy root patch)
mypatch = PdPy(name="simple_patch", root=True)
# initialize some objects and a message box
obj1 = Obj('loadbang')
obj2 = Obj('print')
msg1 = Msg('Hola Mundo!')
# create them in the patch
mypatch.create(obj1).create(msg1).create(obj2)
mypatch.connect(obj1, msg1, obj2)
# write out the patch
mypatch.write()

test_lines = [
  "#N canvas 0 22 450 300 12;",
  "#X obj 12 132 loadbang;",
  "#X msg 12 156 Hola Mundo!;",
  "#X obj 12 180 print;",
  "#X connect 0 0 1 0;",
  "#X connect 1 0 2 0;"
]

with open('simple_patch.pd', 'r') as f:
  for test_line, line in zip(test_lines, f.readlines()):
    assert test_line + "\n" == line
