#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

from .connections import Comm
from .default import Default
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
      super().__init__(*pd_lines[:3], cls=className)
      self.__pdpy__ = self.__class__.__name__
      self.className = self.__cls__
      if 3 < len(pd_lines):
        self.digit_width = pd_lines[3]
        self.limits = Bounds(lower=pd_lines[4], upper=pd_lines[5])
        self.flag = pd_lines[6] if 6 < len(pd_lines) else None
        if 7 < len(pd_lines):
          self.label = pd_lines[7] if Default.label != pd_lines[7] else None
          self.comm = Comm(send=pd_lines[8], receive=pd_lines[9], default=Default.receive)
    elif json_dict is not None:
      super().__populate__(self, json_dict)

  def __pd__(self):
    """ Returns the pd-code representation of the object """
    s = f" {int(getattr(self,'digit_width',Default.digits_width))}"
    if hasattr(self, "limits"):
      s += self.limits.__pd__()
    else:
      s += f" {Default.limits['lower']} {Default.limits['upper']}"
    s += ' ' + int(getattr(self,'flag', Default.flag))
    s += ' ' + getattr(self,'label',Default.label)
    s += f" {self.comm.__pd__(1)}"
    return super().__pd__(s)