#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
import pdpy_lib as pdpy
pd = pdpy.PdPy(name='test_disconnect',root=True)
obj = pdpy.Obj('loadbang')
printer = pdpy.Obj('print')
pd.create(obj, printer)
pd.connect(obj,printer)
pd.__arrange__(pd)
print(pd.__pd__())
pd.disconnect(obj,printer)
print(pd.__pd__())