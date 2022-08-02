#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
from pdpy import PdPy, Obj
# initialize a patch (ie, a pdpy root patch)
mypatch = PdPy(name="audio_example", root=True)
# initialize an oscillator, a multiplier and a dac with 4 channels
obj1 = Obj('osc~').addargs(440)
obj2 = Obj('*~').addargs(0.01)
obj3 = Obj('dac~').addargs([1, 2, 3, 4])
# create them in the patch
mypatch.create(obj1, obj2, obj3)
mypatch.connect(obj1, obj2)
mypatch.connect(obj2, [obj3, 0, 2, 3])
# mypatch.connect(obj2, [obj3, 1])
# write out the patch
mypatch.write()