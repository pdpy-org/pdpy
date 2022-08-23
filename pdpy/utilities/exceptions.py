#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021-22 Fede Camara Halac
# **************************************************************************** #
"""
Exceptions
==========
"""

__all__ = [ 'ArgumentException', 'MalformedName']

class ArgumentException(Exception):
  """ Raise an Argument Exception """
  pass

class MalformedName(Exception):
  """ Raise a Malformed Name Exception """
  pass