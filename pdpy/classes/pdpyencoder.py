#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" PdPyEncoder Class Definition """

from json.encoder import JSONEncoder

__all__ = [ 'PdPyEncoder' ]

class PdPyEncoder(JSONEncoder):
  
  def __init__(self):
    import pdpy
    self.__module__ = pdpy
    # self.__objects__ = []
    # log(1, "PdPyEncoder initialized")

  def __call__(self, __obj__):
    if '__pdpy__' in __obj__:
      __name__ = __obj__['__pdpy__']
      # this line grabs the class from the module
      # and creates an instance of it
      # passing the json object as the argument
      try:
        __class_name__ = getattr(self.__module__, __name__)
        __instance__ = __class_name__(json=__obj__)
        # self.__objects__.append(__class_name__)
        return __instance__
      except Exception as e:
        raise Exception("Error+" +e+". This happened while creating " +__name__+" with PdPyEncoder. Input object: " +__obj__)
    else:
      return __obj__
