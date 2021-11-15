#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

from .pdobj import PdObj
from .classes import Bounds

__all__ = ["PdNativeGui"]

class PdNativeGui(PdObj):
  """ A Pd Native Gui object 
  
  Description
  -----------
  A Pd Native Gui object is a graphical user interface that is implemented in
  pure data. It is a sublcass of the `PdObj`

  Initialization Arguments
  -----------------------
  1. `className`: the name of the class of the object
  2. id: The id of the object
  3. `x`: The x position of the object
  4. `y`: The y position of the object
  5. `digits_width` : The width of the object in digits
  6. lower limit: The lower limit of the object
  7. upper limit: The upper limit of the object
  8. `flag`: The flag of the object
  9. `label`: The label of the object
  10. `receive`: the receiver symbol of the object
  11. `send`: the sender symbol of the object

  """
  def __init__(self, className=None, pd_lines=None, json_dict=None):
    if className is not None and pd_lines is not None:
      super().__init__(*pd_lines[:3])
      self.__pdpy__ = self.__class__.__name__
      self.className = className
      if 3 < len(pd_lines):
        self.digit_width = pd_lines[3]
        self.limits = Bounds(lower=pd_lines[4], upper=pd_lines[5])
        self.flag = pd_lines[6] if 6 < len(pd_lines) else None
        if 7 < len(pd_lines):
          self.label = pd_lines[7] if "-" != pd_lines[7] else None
          self.receive = pd_lines[8] if "-" != pd_lines[8] else None
          self.send = pd_lines[9] if "-" != pd_lines[9] else None
    elif json_dict is not None:
      super().__populate__(self, json_dict)
