#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

from .pdobj import PdObj

__all__ = [
  "PdObject"
]


class PdObject(PdObj):
  """ A Pure Data Object object
  
  Description
  -----------
  This class represents a Pure Data object.

  Initialization Arguments
  ----------
  The first three arguments correspond to the `PdObj` class.
  1. `id`: The id of the pd object.
  2. `x`: The x-coordinate of the pd object.
  3. `y`: The y-coordinate of the pd object.
  4. `className`: The class name of the pd object.
  5. `args`: The argument `list` of the pd object.

  """
  def __init__(self, pd_lines=None,json_dict=None):
    if pd_lines is not None:
      super().__init__(*pd_lines[:3])
      args = list(pd_lines)
      argc = len(args)
      try:
        self.className = args[3] if 3 < argc else None
        self.args = args[4:] if 4 < argc else None
      except:
        raise ValueError("Invalid arguments for PdObject")
        # log(1, self.__json__(), "Can't parse arguments", args)

      self.border = None
    elif json_dict is not None:
      super().__populate__(self, json_dict)

    self.__pdpy__ = self.__class__.__name__
