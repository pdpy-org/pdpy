#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
from pdpy import PdPy, Obj, Msg                # necessary imports
mypatch = PdPy(name="holamundo", root=True)    # a pdpy root patch
obj1 = Obj('loadbang')                         # a loadbang object
obj2 = Obj('print')                            # a print object
msg1 = Msg('Hola Mundo!')                      # a message box with content 
mypatch.create(obj1, msg1, obj2)               # create them in the patch
mypatch.connect(obj1, msg1, obj2)              # connect them in the patch
mypatch.write()                                # write out the patch
