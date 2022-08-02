#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
import pdpy
mypatch = pdpy.Canvas

loadbang = pdpy.Obj
printobj = pdpy.Obj


loadbang.addargs('loadbang')
printobj.addargs('print')

mypatch.add(loadbang)
mypatch.add(printobj)

mypatch.edge()


