#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
""" Touches up the last version, for automated uploads """

from version import get_version

version = get_version(filename="../pyproject.toml")

with open("../../doc/version.txt", "w") as f:
    f.write(".".join(map(lambda x:str(x), version[0])))

