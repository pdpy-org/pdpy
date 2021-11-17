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
  def __init__(self, pd_lines=None, json_dict=None, **kwargs):

    self.__pdpy__ = self.__class__.__name__

    if json_dict is not None:
      super().__init__(**kwargs)
      super().__populate__(self, json_dict)

    elif pd_lines is not None:
      super().__init__(*pd_lines[:3])
      try:
        self.className = pd_lines[3] if 3 < len(pd_lines) else None
        if 4 < len(pd_lines):
          self.addargs(pd_lines[4:])
      except:
        raise ValueError("Invalid arguments for PdObject")
  
  def __pd__(self, args=None):
    """ Return the pd code of the object. """
    if args is None:
      return super().__pd__(self.className)
    else:
      return super().__pd__(args)