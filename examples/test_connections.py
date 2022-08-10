#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
from pdpy import PdPy, Obj, Msg
with PdPy(name="test_connections", root=True) as pd:
  loadbang = Obj('loadbang')
  trigger = Obj('t').addargs('b', 'b')
  until = Obj('until')
  f = Obj('f')
  plus = Obj('+').addargs(1)
  sel = Obj('sel').addargs(99)
  printer = Obj('print')
  msg = Msg('Done')
  pd.create(loadbang, trigger, until, f, plus, sel, printer, msg)
  pd.connect(loadbang, trigger)
  pd.connect(trigger, msg, printer)
  pd.connect([trigger, 1], until)
  pd.connect(until, f, sel)
  pd.connect(f, plus)
  pd.connect(plus, [f, 1])
  pd.connect(sel, [until, 1])
  pd.connect(f, printer)
