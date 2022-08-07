#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Exception Definitions """

__all__ = [ 'ArgumentException', 'MalformedName']

class ArgumentException(Exception):
  pass

class MalformedName(Exception):
  pass