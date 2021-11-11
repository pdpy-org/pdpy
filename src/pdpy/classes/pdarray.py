#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

from .pdobject import PdObject

__all__ = ["PdArray"]

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
    if pd_lines is not None:
      super().__init__(*pd_lines[:4])
      args = list(pd_lines)
      argc = len(args)
      self.subclass = args[4] if 4 < argc else None
      
      off = 0
      if self.subclass is not None:
        if "define" == self.subclass:
          
          if 5 < argc:
            if "-k" == args[5]:
              self.keep = True 
              self.name = args[6] if 6 < argc else None
              off += 1
            else:
              self.name = args[5] if 5 < argc else None
              self.keep = False
          
          if "array" == self.className:
            self.size = int(args[6+off]) if 6+off < argc else None
            off += 1
        
      if 6+off < argc:
        self.args = args[6+off:]

    elif json_dict is not None:
      super().__populate__(self, json_dict)
      
    self.__pdpy__ = self.__class__.__name__
