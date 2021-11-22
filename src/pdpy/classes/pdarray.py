#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

from .pdobject import PdObject

__all__ = [
  "PdArray"
]

class PdArray(PdObject):
  """ A Pure Data array object
  
  Description
  -----------
  This class represents a Pure Data array or text object.

  Initialization Arguments
  ----------
  The first four arguments correspond to the `PdObject` arguments. 
  See the `PdObject` class.
  1. `id`: The id of the pd object.
  2. `x`: The x-coordinate of the pd object.
  3. `y`: The y-coordinate of the pd object.
  4. `className`: The class name of the array.
  5. `subclass`: The sub family of the array, eg. `define` or `sum`, etc.
  6. `-k` flag (optional), or `name`: the name of the array
  7. If it is an `array`, then the remaining argument is the array `size`

  Returns
  -------
  A `PdArray` object.
  
  """
  def __init__(self, pd_lines = None, json_dict = None):

    self.__pdpy__ = self.__class__.__name__

    if json_dict is not None:
      super().__init__(json_dict=json_dict)

    elif pd_lines is not None:
      super().__init__(pd_lines=pd_lines[:4])
      argc = len(pd_lines)

      if 4 < argc:
        setattr(self, 'subclass', pd_lines[4])
        off = 0
        if "define" == self.subclass and 5 < argc and "-k" == pd_lines[5]:
          setattr(self, 'keep', True)
          off += 1
        if 5+off < argc:
          setattr(self, 'name', pd_lines[5+off])
          if "array" == self.className:
            if 6+off < argc:
              setattr(self, 'size', self.num(pd_lines[6+off]))
            off += 1
          if 6+off < argc:
            self.addargs(pd_lines[6+off:])      
  
  def __pd__(self):
    """ Return the pd code of the object. """
    s = ''
    if hasattr(self, 'subclass'):
      s += f"{self.subclass}"
      if hasattr(self, 'keep'):
        s += " -k"
      if hasattr(self, 'name'):
        s += f" {self.name}"
      if "array" == self.className and hasattr(self, 'size'):
        s += f" {self.size}"
    return super().__pd__(s)
