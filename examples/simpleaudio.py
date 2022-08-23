#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
from pdpy import PdPy, Obj                      # necesary imports
mypatch = PdPy(name="simpleaudio", root=True)   # initialize
obj1 = Obj('osc~').addargs(440)                 # an ``osc~`` at 440 Hz
obj2 = Obj('*~').addargs(0.01)                  # a signal multiplier at 0.01
obj3 = Obj('dac~').addargs([1, 2, 3, 4])        # a 4-channel ``dac~``
mypatch.create(obj1, obj2, obj3)                # create them in the patch
mypatch.connect(obj1, obj2)                     # connect ``osc~`` to ``*~``
mypatch.connect(obj2, [obj3, 0, 2, 3])          # connect ``*~`` chans 0,2,3
mypatch.write()                                 # write out the patch