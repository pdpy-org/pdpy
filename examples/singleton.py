#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
import pdpy
with pdpy.PdPy(name='singleton', root=True) as pd:
  bang = pdpy.Bng(size=20, label="mybang", offset={"xoff":30,"yoff":10}, points="20", lbcolor="#555888")
  printer = pdpy.Obj('print')
  pd.create(bang, printer)
  pd.connect(bang, printer)
  pd.write('singleton.json')
