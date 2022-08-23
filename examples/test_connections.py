#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
"""
More Connections
================

This is a counter example that prints numbers 0-99 and a "Done" message.

In this file we see another way to make connections.
Instead of typing ``[trigger, 1]``, we can use a subscript ``trigger[1]``
and we will get the trigger's iolet indexed at ``1``.

We also have here a case where there is a circular conection: ``f`` and ``+``.
In most arrangements, the last object of the circle is placed to the right.


"""
from pdpy import PdPy, Obj, Msg
with PdPy(name="test_connections", root=True) as pd:
  i = 0
  while i < 10:
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
    pd.connect(trigger[1], until) # instead of [trigger, 1]
    pd.connect(until, f, sel)
    pd.connect(f, plus)
    pd.connect(plus, f[1])
    pd.connect(sel, until[1])
    pd.connect(f, printer)
    i += 1
  # pd.write("test_connections.json")

