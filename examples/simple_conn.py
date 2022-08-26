#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
from pdpy_lib import PdPy, Obj, Msg
with PdPy(name="simple_conn", root=True) as pd:
  loadbang = Obj('loadbang')
  trigger = Obj('t').addargs('b', 'b')
  until = Obj('until')
  msg1 = Msg('Hi There...')
  msg2 = Msg('Bye!')
  printer = Obj('print')
  pd.create(loadbang, trigger, msg1, msg2, printer)
  pd.connect([trigger, 1], msg1, printer)
  pd.connect(loadbang, trigger, msg2, printer)
