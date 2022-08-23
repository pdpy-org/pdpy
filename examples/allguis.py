#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
import pdpy

with pdpy.PdPy(name='allguis', root=True) as pd:
  objects = [
    pdpy.Bng(),
    pdpy.Toggle(),
    pdpy.Cnv(),
    pdpy.Nbx(),
    pdpy.Slider(className='vslider'),
    pdpy.Slider(className='hslider'),
    pdpy.Radio(className='hradio'),
    pdpy.Radio(className='vradio'),
    pdpy.Vu(),
    pdpy.Gui(className='float'),
    pdpy.Gui(className='symbol'),
    pdpy.Gui(className='list'),
  ]
  pd.create(*objects)
