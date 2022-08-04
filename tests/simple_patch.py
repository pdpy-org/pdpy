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